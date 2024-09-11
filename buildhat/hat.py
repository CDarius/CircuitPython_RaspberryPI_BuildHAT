import io
import sys
import busio
import time
import digitalio
import microcontroller
import asyncio

from .models.devicetype import DeviceType
from .models.utils import validate_port
import buildhat.device
import buildhat.activedevice
import buildhat.motors.activemotor
import buildhat.motors.passivemotor
import buildhat.devices.colorsensor
import buildhat.devices.ultrasonicdistancesensor
import buildhat.devices.colordistancesensor
import buildhat.devices.lightmatrix

try:
    from typing import Callable, Dict
except:
    pass

_FIRMWARE = "Firmware version: "
_BOOTLOADER = "BuildHAT bootloader version"
_DONE = "Done initialising ports"
_PROMPT = "BHBL>"
_CONNECTED = ": connected to active ID"
_CONNECTEDPASSIVE = ": connected to passive ID"
_DISCONNECTED = ": disconnected"
_DEVTIMEOUT = ": timeout during data phase: disconnecting"
_NOTCONNECTED = ": no device detected"


class Hat:
    def __init__(
        self,
        tx: microcontroller.Pin,
        rx: microcontroller.Pin,
        reset: microcontroller.Pin,
        receiver_buffer_size=2048,
        debug: bool = False,
    ):
        self._serial = busio.UART(
            tx=tx,
            rx=rx,
            baudrate=115200,
            parity=None,
            bits=8,
            stop=1,
            receiver_buffer_size=receiver_buffer_size,
        )
        self._serial.timeout = 0.1

        self._reset_out = digitalio.DigitalInOut(reset)
        self._reset_out.direction = digitalio.Direction.OUTPUT
        self._reset_out.value = True

        self._debug = debug

        # 4 ports, can be any of motors, sensors, active elements.
        self._connected_devices = [None] * 4

        # stack of functions coming from devices and waiting for a specific message
        self._device_message_handlers: Dict[
            buildhat.device.Device, Callable[[str], bool]
        ] = {}

        # lock for reading vin message
        self._vin_lock = asyncio.Lock()
        self._last_vin_read = 0.0

        # The first command sent after UART creation always fails. I guess
        # that is a firmware bug. Let's send a non requested command as
        # a workaround
        try:
            self._serial.write(b"version\r")
            for i in range(3):
                self._serial.readline()
        except:
            raise Exception("Failed to start serial communication with Build Hat")

        firmware_loaded = self._init_hat()

        if self._debug:
            print("Build Hat initialization done")

        self.led_mode = "voltage"

        # update connected devices
        if self._debug:
            print("Waiting for devices to connect...")
        if not firmware_loaded:
            self._serial.write(b"list\r")
            while not self._serial.in_waiting:
                pass
            time.sleep(0.1)
            self._process_all_incoming_messages()
        else:
            # It takes up to 10 seconds the BuildHat to connect to all devices
            end_time = time.monotonic_ns() + 10 * 1e9
            while time.monotonic_ns() < end_time:
                self._process_all_incoming_messages()

        if self._debug:
            print("Device discovery completed")

    def deinit(self):
        if self.serial:
            self.stop_all_devices()
            self.serial.deinit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.deinit()

    def __del__(self):
        print("Destructo called")
        self.stop_all_devices()

    @property
    def serial(self) -> busio.UART:
        return self._serial

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        self._debug = value

    def _init_hat(self) -> None:
        # Check if we're in the bootloader or the firmware
        status = ""
        attempt = 10
        self._serial.reset_input_buffer()
        self._serial.write(b"version\r")
        while not status:
            line = self.readline(skip="version")
            if self._debug and line:
                print(line)

            if line and line.startswith(_FIRMWARE):
                hat_version = line[len(_FIRMWARE) :].split(" ")
                file_version = self._get_firmware_file_version()
                if int(hat_version[0]) == file_version:
                    status = "firmare_ok"
                else:
                    status = "need_new_firmware"
            elif line and line.startswith(_BOOTLOADER):
                status = "bootloader"
            elif attempt == 0:
                if not line:
                    raise Exception(
                        "Build Hat Initialization failed: No answer received for version command"
                    )
                else:
                    raise Exception("Unknown Build Hat status  (bootloader/firmware)")

            attempt -= 1

        if status == "need_new_firmware":
            self._reset_hat()
            self._load_firmware()
            return True
        elif status == "bootloader":
            self._load_firmware()
            return True

        return False

    @property
    def _firmware_folder(self) -> str:
        """Return the path of the folder that contains BuildHAT firmware files"""
        return f"{sys.modules['buildhat'].__path__}/data"

    def _get_firmware_file_version(self) -> int:
        """Read the version of the firmware in _firmware_folder

        :return Firmware version
        """
        with open(f"{self._firmware_folder}/version", "r") as file:
            return int(file.read())

    def _reset_hat(self):
        """Reset the HAT"""
        self._reset_out.value = 0
        time.sleep(0.01)
        self._reset_out.value = 1
        time.sleep(0.01)
        self._reset_out.value = 0
        time.sleep(0.5)

    def _load_firmware(self):
        """Load firmware from _firmware_folder folder in the hat"""
        firmware_folder = self._firmware_folder
        firmware_file = f"{firmware_folder}/firmware.bin"
        signature_file = f"{firmware_folder}/signature.bin"

        # Calculate file leght and checksum
        if self._debug:
            print("Calculating firmware checksum...")
        try:
            with open(firmware_file, "rb") as f:
                fimware_len, firmware_checksum = self._checksum(f)
        except Exception as e:
            raise Exception(
                f"Build Hat firmare load failed: failed to read '{firmware_file}'"
            ) from e

        # Load firmaware file in the hat
        if self._debug:
            print("Loading firmware into the hat...")
        try:
            self._serial.write(b"clear\r")
            self._get_prompt()
            self._serial.write(f"load {fimware_len} {firmware_checksum}\r".encode())
            time.sleep(0.1)
            # STX = 0x02
            self._serial.write(b"\x02")
            with open(firmware_file, "rb") as f:
                data = f.read(1024)
                while len(data) > 0:
                    self._serial.write(data)
                    data = f.read(1024)
            # ETX = 0x03
            self._serial.write(b"\x03\r")
            self._get_prompt()
        except Exception as e:
            raise Exception(
                "Build Hat firmare load failed: failed to load fimware file in the hat"
            ) from e

        try:
            with open(signature_file, "rb") as f:
                sig = f.read()
        except Exception as e:
            raise Exception(
                f"Build Hat firmare load failed: failed to read '{signature_file}'"
            ) from e

        # Load signature file in the hat
        if self._debug:
            print("Loading firmware signature int the hat...")
        try:
            self._serial.write(f"signature {len(sig)}\r".encode())
            time.sleep(0.1)
            # STX = 0x02
            self._serial.write(b"\x02")
            self._serial.write(sig)
            # ETX = 0x03
            self._serial.write(b"\x03\r")
        except Exception as e:
            raise Exception(
                "Build Hat firmare load failed: failed to load signature file in the hat"
            ) from e

        # Wait for build hat serial prompt
        if self._debug:
            print("Wait for hat serial pomprt ...")
        try:
            self._get_prompt()
        except Exception as e:
            raise Exception(
                "Build Hat firmare load failed: failed to reach serial prompt"
            ) from e

        # Reboot the hat and wait for done message
        if self._debug:
            print("Reboot the the hat and wait for done message...")
        self._serial.write(b"reboot\r")
        try:
            self._wait_for_message(_DONE, timeout_ms=5000)
        except:
            raise Exception(
                "Build Hat firmare load failed: done message not received after reboot"
            )

        if self._debug:
            print("Firmware loading completed")

    def _checksum(self, file: io.FileIO):
        """Calculate checksum from data

        :param file: File to calculate the checksum from
        :return: File lenght in bytes and file checksum
        """
        file_lenght = 0
        checksum = 1

        file.seek(0)
        data = file.read(1024)
        while len(data) > 0:
            file_lenght += len(data)
            for i in range(0, len(data)):
                if (checksum & 0x80000000) != 0:
                    checksum = (checksum << 1) ^ 0x1D872B41
                else:
                    checksum = checksum << 1
                checksum = (checksum ^ data[i]) & 0xFFFFFFFF
            data = file.read(1024)

        return (file_lenght, checksum)

    def readline(self, skip=None) -> str | None:
        """Read data from the serial port of Build HAT

        :return: Line that has been read
        """
        line = self._serial.readline()
        if line:
            line = line.decode("utf-8", "ignore").rstrip()

            if skip and skip == line:
                return self.readline(skip=skip)

            return line
        return None

    def _get_prompt(self, timeout_ms: int = 2000) -> None:
        """Loop until prompt is found

        :param timeout_ms: max time to wait for the prompt. The 0 value disable the timeout check
        """
        try:
            self._wait_for_message(_PROMPT, timeout_ms=timeout_ms)
        except:
            raise Exception("Timeout waiting for Buit Hat prompt")

    def _wait_for_message(self, message: str, timeout_ms: int = 2000) -> None:
        """Loop until message is found

        :param message: message from the hat to wait for
        :param timeout_ms: max time to wait for the prompt. The 0 value disable the timeout check
        """
        start_time = time.monotonic_ns()
        timeout_ns = timeout_ms * 1e6
        while True:
            try:
                line = self.readline()
            except:
                line = None

            if line and line.startswith(message):
                break
            if timeout_ns > 0:
                delta = time.monotonic_ns() - start_time
                if delta > timeout_ns:
                    raise Exception(f"Timeout waiting for Buit Hat message: {message}")

    def update(self) -> None:
        """Process all the next incoming messages from the hat"""
        self._process_all_incoming_messages()

    def _process_all_incoming_messages(self) -> None:
        """Process all the incoming messages from the hat"""
        while self._serial.in_waiting:
            line = self.readline()
            try:
                self._process_message(line)
            except:
                if self._debug:
                    print(f"FAILED TO PROCESS INCOMING MESSAGE: {line}")

    def _process_message(self, line: str) -> None:
        processed = True
        if not line:
            return
        elif line[0] == "P" and line[2] == ":":
            port = int(line[1])
            msg = line[2:]
            if 0 <= port < 4:
                if msg.startswith(_CONNECTED) or msg.startswith(_CONNECTEDPASSIVE):
                    active = msg.startswith(_CONNECTED)
                    typeid = int(msg.split(" ")[-1], 16)

                    if self._debug:
                        print(
                            f"{'Active' if active else 'Passive'} device connected. Port={port} Id={hex(typeid)}"
                        )

                    if DeviceType.is_motor(typeid):
                        if active:
                            self._connected_devices[
                                port
                            ] = buildhat.motors.activemotor.ActiveMotor(
                                self, port, typeid
                            )
                        else:
                            self._connected_devices[
                                port
                            ] = buildhat.motors.passivemotor.PassiveMotor(
                                self, port, typeid
                            )
                    else:
                        if active:
                            if typeid == DeviceType.SPIKE_COLOR_SENSOR:
                                self._connected_devices[
                                    port
                                ] = buildhat.devices.colorsensor.ColorSensor(
                                    self, port, typeid
                                )
                            elif typeid == DeviceType.SPIKE_ULTRASONIC_DISTANCE_SENSOR:
                                self._connected_devices[
                                    port
                                ] = buildhat.devices.ultrasonicdistancesensor.UltrasonicDistanceSensor(
                                    self, port, typeid
                                )
                            elif typeid == DeviceType.COLOR_AND_DISTANCE_SENSOR:
                                self._connected_devices[
                                    port
                                ] = buildhat.devices.colordistancesensor.ColorDistanceSensor(
                                    self, port, typeid
                                )
                            elif typeid == DeviceType.SPIKE_3X3_COLOR_LIGHT_MATRIX:
                                self._connected_devices[
                                    port
                                ] = buildhat.devices.lightmatrix.LightMatrix(
                                    self, port, typeid
                                )
                            else:
                                self._connected_devices[
                                    port
                                ] = buildhat.activedevice.ActiveDevice(
                                    self, port, typeid
                                )
                        else:
                            self._connected_devices[port] = buildhat.device.Device(
                                self, port, typeid
                            )
                elif (
                    msg.startswith(_DISCONNECTED)
                    or msg.startswith(_DEVTIMEOUT)
                    or msg.startswith(_NOTCONNECTED)
                ):
                    if self._connected_devices[port]:
                        device = self._connected_devices[port]
                        self._connected_devices[port] = None
                        if isinstance(device, buildhat.device.Device):
                            if device in self._device_message_handlers:
                                del self._device_message_handlers[device]
                            device.on_disconnect()

                        if self.debug:
                            print(f"Deviced Id={device.type} disconnected")
                else:
                    processed = False

        elif line[0] == "P" and (line[2] == "C" or line[2] == "M"):
            header, values = line.split(":")
            port = int(header[1])
            iscombi = header[2] == "C"
            mode = int(header[3:])
            device = self._connected_devices[port]
            if isinstance(device, buildhat.activedevice.ActiveDevice):
                if iscombi:
                    values = [v for v in values.split(" ") if v]
                    device.on_combi_value_update(mode, values)
                else:
                    value = values.strip()
                    device.on_single_value_update(mode, value)
        else:
            processed = False

        if processed:
            return

        # Try to process the message with _device_message_handlers
        for dev, handler in self._device_message_handlers.items():
            if handler(line):
                del self._device_message_handlers[dev]
                return

        # Test if is a vin message
        if self._vin_lock.locked():
            if (
                len(line) >= 5
                and (line[1] == "." or line[2] == ".")
                and line.endswith(" V")
            ):
                self._last_vin_read = float(line.split(" ")[0])
                if self._vin_lock.locked():
                    self._vin_lock.release()
                return

        if self._debug:
            print(f"UNKNOWN LINE: {line}")

    def get_device(self, port: int) -> buildhat.device.Device:
        validate_port(port)
        return self._connected_devices[port]

    def push_device_message_handle(
        self, device: buildhat.device.Device, handler: Callable[[str], bool]
    ) -> None:
        self._device_message_handlers[device] = handler

    def pop_device_message_handle(self, device: buildhat.device.Device) -> None:
        del self._device_message_handlers[device]

    def stop_all_devices(self):
        for d in self._connected_devices:
            if isinstance(d, buildhat.device.Device):
                try:
                    d.off()
                except:
                    pass

    async def vin(self):
        """Get the voltage present on the input power jack

        :return: Voltage on the input power jack
        :rtype: float
        """
        await self._vin_lock.acquire()
        self._serial.write(b"vin\r")
        # Wait for the lock to be released by the message loop
        async with self._vin_lock:
            pass

        return self._last_vin_read

    @property
    def led_mode(self) -> str:
        """BuildHat leds mode
        By default the color depends on the input voltage with green being nominal at around 8V
        (The fastest time the LEDs can be perceptually toggled is around 0.025 seconds)

        Mode values: orange, green, both, off, or voltage (default)
        """
        return self._led_mode

    @led_mode.setter
    def led_mode(self, color) -> None:
        if color == "orange":
            mode = 1
        elif color == "green":
            mode = 2
        elif color == "both":
            mode = 3
        elif color == "off":
            mode = 0
        elif color == "voltage":
            mode = -1
        else:
            return

        self._serial.write(f"ledmode {mode}\r".encode())
        self._led_mode = color

    async def clear_faults(self) -> None:
        """Clear all motors latched faults"""
        self._serial.write(b"clear_faults\r")
        await asyncio.sleep(2)
