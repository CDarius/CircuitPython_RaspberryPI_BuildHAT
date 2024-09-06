import buildhat.hat
from .models.devicetype import DeviceType


class Device:
    def __init__(self, hat: buildhat.hat.Hat, port: str, type: DeviceType):
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
        except:
            pass

        self._is_connected = False

    @property
    def hat(self) -> buildhat.hat.Hat:
        return self._hat

    @property
    def port(self) -> str:
        return self._port

    @property
    def type(self) -> DeviceType:
        return self._type

    @property
    def is_connected(self) -> bool:
        "True when the sensor is connected at th build hat"
        return self._is_connected

    @property
    def name(self) -> str:
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
        """Raise an exception if the sensor is not connected"""
        if not self._is_connected:
            raise Exception("No device connected")

    def _write1(self, data: bytearray) -> None:
        hexstr = " ".join(f"{h:x}" for h in data)
        self.hat.serial.write(f"port {self._port} ; write1 {hexstr}\r")
