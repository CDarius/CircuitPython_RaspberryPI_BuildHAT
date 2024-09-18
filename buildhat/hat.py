# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT
"""
CircuitPython driver for RaspberryPi Build HAT


* Author(s): Dario Cammi

Implementation Notes
--------------------

**Hardware:**

* `RaspberryPi Build HAT <https://www.adafruit.com/product/5287>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* AsyncIO library: https://github.com/adafruit/Adafruit_CircuitPython_asyncio
"""

import asyncio

import microcontroller

from .activedevice import ActiveDevice
from .device import Device
from .devices.colordistancesensor import ColorDistanceSensor
from .devices.colorsensor import ColorSensor
from .devices.lightmatrix import LightMatrix
from .devices.ultrasonicdistancesensor import UltrasonicDistanceSensor
from .hatserialcomm import HatSerialCommunication
from .models.devicetype import DeviceType
from .models.utils import validate_port
from .motors.activemotor import ActiveMotor
from .motors.passivemotor import PassiveMotor

_CONNECTED = ": connected to active ID"
_CONNECTEDPASSIVE = ": connected to passive ID"
_DISCONNECTED = ": disconnected"
_DEVTIMEOUT = ": timeout during data phase: disconnecting"
_NOTCONNECTED = ": no device detected"

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/CDarius/CircuitPython_RaspberryPi_BuildHAT.git"


class Hat(HatSerialCommunication):
    """CircuitPython driver for RaspberryPI Build HAT

    :param microcontroller.Pin tx: Transmit pin used for serial communication with the HAT
    :param microcontroller.Pin rx: Receive pin used for serial communication with the HAT
    :param microcontroller.Pin reset: Reset output pin connected to the hat
    :param int intreceiver_buffer_size: Serial bus receive buffer
    :param bool debug: When `True` print to the output console the all the hat initialization steps plus other information
        about the communication with the hat

    This library let you control Lego® devices (motors, distance sensors, color sensors, etc...)
    through the RaspberryPI Build HAT.

    .. important:: The first time that the Build HAT library starts need to load the firmware in the HAT.
        It takes about 30 seconds to load the firmware and restart the HAT.
        Please wait until the firmware is loaded without interrupting the execution

    Connect a CircuitPython device to the RaspberryPI Build HAT require just 4 for wire:

    ======================  =========
    CircuitPython board     Build HAT
    ======================  =========
    Serial TX               GPIO 14
    Serial RX               GPIO 15
    Digital output (reset)  GPIO 4
    GND                     GND
    ======================  =========

    .. tip:: It is also possible to use the 5V from the Build HAT to power the CircuitPython board.

    """

    def __init__(
        self,
        tx: microcontroller.Pin,
        rx: microcontroller.Pin,
        reset: microcontroller.Pin,
        receiver_buffer_size: int = 2048,
        debug: bool = False,
    ):
        # 4 ports, can be any of motors, sensors, active elements.
        self._connected_devices = [None] * 4

        # lock for reading vin message
        self._vin_lock = asyncio.Lock()
        self._last_vin_read = 0.0

        super().__init__(tx, rx, reset, receiver_buffer_size, debug)

    def deinit(self):
        """Stop all devices and release the serial bus device"""
        if self.serial:
            self.stop_all_devices()

        super().deinit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.deinit()

    def __del__(self):
        self.stop_all_devices()

    def update(self) -> None:
        """Process all the incoming messages from the hat

        .. important:: In order to process all the hat messages this function must be called in a loop. Don't use functions
            like `time.sleep` that block the code execution and prevent update to process the messages

        Once the instance of :py:class:`Hat` is created the :py:meth:`update` method should be called in an async loop:

        .. code-block:: python

            import board
            import asyncio
            from buildhat.hat import Hat

            buildhat = Hat(tx=board.TX, rx=board.RX, reset=board.GP23)

            # Update loop to process hat messages
            async def buildhat_loop(hat):
                while True:
                    hat.update()
                    await asyncio.sleep(0)

            # Your program loop
            async def program_loop(hat):
                while True:
                    # Put you program code loop here. For example here you can
                    # start a motor, read a color etc...
                    await asyncio.sleep(0)

            async def main():
                buildhat_loop_task = asyncio.create_task(buildhat_loop(buildhat))
                program_loop_task = asyncio.create_task(program_loop(buildhat))

                await asyncio.gather(buildhat_loop_task, program_loop_task)

            asyncio.run(main())

        """
        self._process_all_incoming_messages()

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
                        print(f"{'Active' if active else 'Passive'} device connected. Port={port} Id={hex(typeid)}")

                    if DeviceType.is_motor(typeid):
                        if active:
                            self._connected_devices[port] = ActiveMotor(self, port, typeid)
                        else:
                            self._connected_devices[port] = PassiveMotor(self, port, typeid)
                    elif active:
                        if typeid == DeviceType.SPIKE_COLOR_SENSOR:
                            self._connected_devices[port] = ColorSensor(self, port, typeid)
                        elif typeid == DeviceType.SPIKE_ULTRASONIC_DISTANCE_SENSOR:
                            self._connected_devices[port] = UltrasonicDistanceSensor(self, port, typeid)
                        elif typeid == DeviceType.COLOR_AND_DISTANCE_SENSOR:
                            self._connected_devices[port] = ColorDistanceSensor(self, port, typeid)
                        elif typeid == DeviceType.SPIKE_3X3_COLOR_LIGHT_MATRIX:
                            self._connected_devices[port] = LightMatrix(self, port, typeid)
                        else:
                            self._connected_devices[port] = ActiveDevice(self, port, typeid)
                    else:
                        self._connected_devices[port] = Device(self, port, typeid)
                elif msg.startswith(_DISCONNECTED) or msg.startswith(_DEVTIMEOUT) or msg.startswith(_NOTCONNECTED):
                    if self._connected_devices[port]:
                        device = self._connected_devices[port]
                        self._connected_devices[port] = None
                        if isinstance(device, Device):
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
            if isinstance(device, ActiveDevice):
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
            if len(line) >= 5 and (line[1] == "." or line[2] == ".") and line.endswith(" V"):
                self._last_vin_read = float(line.split(" ")[0])
                if self._vin_lock.locked():
                    self._vin_lock.release()
                return

        if self._debug:
            print(f"UNKNOWN LINE: {line}")

    def get_device(self, port: int) -> Device:
        """Return the device connected to a specific port

        :param port: Build HAT port. Range 0 to 3

        Once a Lego® device is connected to a Build HAT port it send a "connected" message. When the
        library receive this message, parse its information and create an instace of the device (motor,
        color sensor, distance sensor, etc...). The instance of the discovered device can be obtained
        through this method. See :doc:`Examples<examples>`
        """
        validate_port(port)
        return self._connected_devices[port]

    def stop_all_devices(self):
        """Stop all devices connected to the hat"""
        for d in self._connected_devices:
            if isinstance(d, Device):
                try:
                    d.off()
                except Exception:
                    pass

    async def vin(self) -> float:
        """Get the voltage present on the input power jack in Volt

        :return: Voltage on the input power jack

        Example code:

        .. code-block:: python

            import board
            import asyncio
            from buildhat.hat import Hat

            buildhat = Hat(tx=board.TX, rx=board.RX, reset=board.GP23, debug=True)

            async def buildhat_loop(hat):
                while True:
                    hat.update()
                    await asyncio.sleep(0)

            async def voltage_loop(hat):
                while True:
                    voltage = await hat.vin()
                    print(f"Voltage: {voltage}V")
                    await asyncio.sleep(1)

            async def main():
                buildhat_loop_task = asyncio.create_task(buildhat_loop(buildhat))
                voltage_loop_task = asyncio.create_task(voltage_loop(buildhat))

                await asyncio.gather(buildhat_loop_task, voltage_loop_task)

            asyncio.run(main())
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

        ===========  ===================================  =================================
        Mode values  Orange led                           Green led
        ===========  ===================================  =================================
        ``orange``   on                                   off
        ``green``    off                                  on
        ``both``     on                                   on
        ``off``      off                                  off
        ``voltage``  on when undervoltage or overvoltage  on when voltage is ok (aroung 8V)
        ===========  ===================================  =================================
        """
        return self._led_mode

    @led_mode.setter
    def led_mode(self, color) -> None:
        if not isinstance(color, str):
            raise ValueError("Color must be a string")
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
            raise ValueError("Invalid led mode")

        self._serial.write(f"ledmode {mode}\r".encode())
        self._led_mode = color

    async def clear_faults(self) -> None:
        """Clear all motors latched faults"""
        self._serial.write(b"clear_faults\r")
        await asyncio.sleep(2)
