import buildhat.hat
from ..models.devicetype import DeviceType
from ..activedevice import ActiveDevice

class UltrasonicDistanceSensor(ActiveDevice):
    """Distance sensor
    Part number: 6302968
    """

    def __init__(self, hat: buildhat.hat.Hat, port: str, type: DeviceType):
        super().__init__(hat, port, type)
        self._distance = -1
        self.on()
        self.select_read_mode(0)

    def on(self):
        """Turn on the device"""
        self.hat.serial.write(f"port {self.port} ; set -1\r")

    @property
    def distance(self) -> int:
        """Distance in mm"""
        return self._distance

    def eyes(self, *args: int) -> None:
        """
        Brightness of LEDs on sensor

        If len(args) == 1 all led are set to the same brightness value
        If len(args) == 4 leds are set in this order: upper right, upper left, lower right, lower left

        :param args: One or four brightness arguments of 0 to 100
        :raises DistanceSensorError: Occurs if invalid brightness passed
        """
        out = bytearray(5)
        out[0] = 0xC5
        values = None
        if len(args) == 1:
            values = [args[0]] * 4
        elif len(args) == 4:
            values = args
        else:
            raise ValueError("Need 1 or 4 brightness value in range 0 to 100")

        for i in range(4):
            v = values[i]
            if not (v >= 0 and v <= 100):
                raise ValueError("Need 1 or 4 brightness value in range 0 to 100")
            out[i + 1] = v

        self._write1(out)

    def on_single_value_update(self, mode: int, value: str) -> None:
        if mode == 0:
            self._distance = int(value)
