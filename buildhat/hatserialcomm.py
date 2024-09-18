# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

import io
import sys
import time

import busio
import digitalio
import microcontroller

try:
    from typing import Callable, Dict
except ImportError:
    pass

_FIRMWARE = "Firmware version: "
_BOOTLOADER = "BuildHAT bootloader version"
_DONE = "Done initialising ports"
_PROMPT = "BHBL>"


class HatSerialCommunication:
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

        # stack of functions coming from devices and waiting for a specific message
        self._device_message_handlers: Dict[object, Callable[[str], bool]] = {}

        # The first command sent after UART creation always fails. I guess
        # that is a firmware bug. Let's send a non requested command as
        # a workaround
        try:
            self._serial.write(b"version\r")
            for i in range(3):
                self._serial.readline()
        except Exception as e:
            raise Exception("Failed to start serial communication with Build Hat") from e

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
            self.serial.deinit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.deinit()

    @property
    def serial(self) -> busio.UART:
        """Serial bus connected to the hat"""
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
                    raise Exception("Build Hat Initialization failed: No answer received for version command")
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
        with open(f"{self._firmware_folder}/version") as file:
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
            raise Exception(f"Build Hat firmare load failed: failed to read '{firmware_file}'") from e

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
            raise Exception("Build Hat firmare load failed: failed to load fimware file in the hat") from e

        try:
            with open(signature_file, "rb") as f:
                sig = f.read()
        except Exception as e:
            raise Exception(f"Build Hat firmare load failed: failed to read '{signature_file}'") from e

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
            raise Exception("Build Hat firmare load failed: failed to load signature file in the hat") from e

        # Wait for build hat serial prompt
        if self._debug:
            print("Wait for hat serial pomprt ...")
        try:
            self._get_prompt()
        except Exception:
            raise Exception("Build Hat firmare load failed: failed to reach serial prompt")

        # Reboot the hat and wait for done message
        if self._debug:
            print("Reboot the the hat and wait for done message...")
        self._serial.write(b"reboot\r")
        try:
            self._wait_for_message(_DONE, timeout_ms=5000)
        except Exception:
            raise Exception("Build Hat firmare load failed: done message not received after reboot")

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

    def readline(self, skip: str = None) -> str | None:
        """Read on line from the serial port of Build HAT

        :param skip: Line string to skip
        :return: Line that has been read
        """
        line = self._serial.readline()
        if line:
            line = line.decode("utf-8", "ignore")
            if line:
                line = line.rstrip()

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
        except Exception:
            raise Exception("Timeout waiting for Buit Hat prompt")

    def _wait_for_message(self, message: str, timeout_ms: int = 2000) -> None:
        """Loop until message is found

        :param message: message from the hat to wait for
        :param timeout_ms: max time to wait for the prompt. The 0 value disable the timeout check
        """
        start_time = time.monotonic_ns()
        timeout_ns = timeout_ms * 1e6
        while True:
            line = self.readline()

            if line and line.startswith(message):
                break
            if timeout_ns > 0:
                delta = time.monotonic_ns() - start_time
                if delta > timeout_ns:
                    raise Exception(f"Timeout waiting for Buit Hat message: {message}")

    def _process_all_incoming_messages(self) -> None:
        """Process all the incoming messages from the hat"""
        while self._serial.in_waiting:
            line = self.readline()
            try:
                self._process_message(line)
            except Exception as e:
                print(e)
                if self._debug:
                    print(f"FAILED TO PROCESS INCOMING MESSAGE: {line}")

    def _process_message(self, line: str) -> None:
        pass

    def push_device_message_handle(self, device: object, handler: Callable[[str], bool]) -> None:
        self._device_message_handlers[device] = handler

    def pop_device_message_handle(self, device: object) -> None:
        del self._device_message_handlers[device]
