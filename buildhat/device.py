# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT
"""
`Device`
"""

from .hatserialcomm import HatSerialCommunication
from .models.devicetype import DeviceType


class Device:
    """A generic Lego® device (motor, color sensor, distance sensor, etc..)

    It can be either a passive device on an active device
    """

    def __init__(self, hat: HatSerialCommunication, port: int, type: int):
        self._hat = hat
        self._port = port
        self._type = type
        self._is_connected = True

        if self._hat.debug:
            print(f"Type={DeviceType.get_name(self._type)}")

    def deinit(self) -> None:
        try:
            if self._is_connected:
                self.off()
        except ImportError:
            pass

        self._is_connected = False

    @property
    def hat(self) -> HatSerialCommunication:
        """Return a Build HAT instace"""
        return self._hat

    @property
    def port(self) -> str:
        """Return the hat port where the device is connected"""
        return self._port

    @property
    def type(self) -> int:
        """Return the device type it

        See :py:class:`DeviceType<buildhat.models.devicetype.DeviceType>`
        """
        return self._type

    @property
    def is_connected(self) -> bool:
        """Return `True` when the device is connected at th build hat or `False` when it disconnected"""
        return self._is_connected

    @property
    def name(self) -> str:
        """Return the device name"""
        return DeviceType.get_name(self._type)

    def on_disconnect(self) -> None:
        """Function called when the device disconnet from build hat"""
        self._is_connected = False
        self.deinit()

    def on(self) -> None:
        """Turn on the device"""
        self.hat.serial.write(f"port {self._port} ; port_plimit 1 ; on\r")

    def off(self) -> None:
        """Turn off the device"""
        self.hat.serial.write(f"port {self._port} ; off\r")

    def ensure_connected(self) -> None:
        """Test if the device is connected and raise an exception if it is not"""
        if not self._is_connected:
            raise Exception("No device connected")

    def _write1(self, data: bytearray) -> None:
        hexstr = " ".join(f"{h:x}" for h in data)
        self.hat.serial.write(f"port {self._port} ; write1 {hexstr}\r")
