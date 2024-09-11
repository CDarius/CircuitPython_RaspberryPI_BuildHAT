import math
import asyncio

import buildhat.hat
from ..models.devicetype import DeviceType
from ..activedevice import ActiveDevice
from .color import Color

try:
    from typing import List, Tuple
except:
    pass


class ColorSensor(ActiveDevice):
    """Color sensor
    Part number: 6217705
    """

    def __init__(self, hat: buildhat.hat.Hat, port: str, type: DeviceType):
        super().__init__(hat, port, type)

        self._read_lock = asyncio.Lock()

        self._is_on = False
        self.num_read_average = 4
        self.select_read_mode(0)

    @property
    def num_read_average(self) -> int:
        """Number of reads to compute the average result"""
        return self._num_read_average

    @num_read_average.setter
    def num_read_average(self, num: int) -> None:
        if 1 <= num <= 25:
            self._num_read_average = num
        else:
            raise ValueError("Parameter num should be in range 1-25")

    def on(self) -> None:
        """Turn on the device"""
        self.hat.serial.write(f"port {self._port} ; port_plimit 1 ; set -1\r")
        self._is_on = True

    def off(self) -> None:
        """Turn off the device"""
        super().off()
        self._is_on = False

    def _turn_on(self) -> None:
        """Turn the device on if it is not on"""
        if not self._is_on:
            self.on()

    def _turn_off(self) -> None:
        """Turn the device off if it is not off"""
        if not self._is_on:
            self.off()

    async def get_color(self) -> Color:
        """Make multiple color reads and return the average in RBI format
        It takes num_read_average reads to compute the average value

        :return: Color value
        """
        r, g, b, _ = await self.get_color_rgbi()
        return Color.get_color_from_rgb(r, g, b)

    async def get_color_rgbi(self) -> Tuple[int, int, int, int]:
        """Read the average color in RGBI format
        It takes num_read_average reads to compute the average value

        :return: RGBI values
        """
        self.ensure_connected()

        self._turn_on()
        self.select_read_mode(5)  # RGB I

        reads = []
        while len(reads) < self._num_read_average:
            update = await self._wait_for_one_update()
            if len(update) == 4:
                reads.append(update)
        return self._avgrgbi(reads)

    def _avgrgbi(
        self, reads: List[Tuple[int, int, int, int]]
    ) -> Tuple[int, int, int, int]:
        readings = []
        for read in reads:
            read = [
                int((read[0] / 1024) * 255),
                int((read[1] / 1024) * 255),
                int((read[2] / 1024) * 255),
                int((read[3] / 1024) * 255),
            ]
            readings.append(read)
        return (
            int(sum([rgbi[0] for rgbi in readings]) / len(readings)),
            int(sum([rgbi[1] for rgbi in readings]) / len(readings)),
            int(sum([rgbi[2] for rgbi in readings]) / len(readings)),
            int(sum([rgbi[3] for rgbi in readings]) / len(readings)),
        )

    async def get_color_hsv(self) -> Tuple[int, int, int]:
        """Make multiple color reads and return the average in HSV format
        It takes num_read_average reads to compute the average value

        :return: HSV representation
        """
        self.ensure_connected()

        self._turn_on()
        self.select_read_mode(6)  # HSV

        readings = []
        while len(readings) < self._num_read_average:
            read = await self._wait_for_one_update()
            if len(read) == 3:
                read = [
                    read[0],
                    int((read[1] / 1024) * 100),
                    int((read[2] / 1024) * 100),
                ]
                readings.append(read)
        s = c = 0
        for hsv in readings:
            hue = hsv[0]
            s += math.sin(math.radians(hue))
            c += math.cos(math.radians(hue))

        hue = int((math.degrees((math.atan2(s, c))) + 360) % 360)
        sat = int(sum([hsv[1] for hsv in readings]) / len(readings))
        val = int(sum([hsv[2] for hsv in readings]) / len(readings))
        return (hue, sat, val)

    async def get_ambient_light(self) -> int:
        """Return the average ambient light in range 0-100
        It takes num_read_average reads to compute the average value

        :return: Ambient light
        """
        self.ensure_connected()

        self._turn_off()
        self.select_read_mode(2)  # AMBI

        reads = []
        while len(reads) < self._num_read_average:
            update = await self._wait_for_one_update()
            if len(update) == 1:
                reads.append(update[0])

        return int(sum(reads) / self._num_read_average)

    async def get_reflected_light(self) -> int:
        """Return the average reflected light in range 0-100
        It takes num_read_average reads to compute the average value

        :return: Reflected light
        """
        self.ensure_connected()

        self._turn_on()
        self.select_read_mode(1)  # REFLT

        reads = []
        while len(reads) < self._num_read_average:
            update = await self._wait_for_one_update()
            if len(update) == 1:
                reads.append(update[0])

        return int(sum(reads) / self._num_read_average)

    async def _wait_for_one_update(self) -> List[int]:
        await self._read_lock.acquire()
        # Wait for the lock to be released on next update in on_single_value_update
        async with self._read_lock:
            pass
        try:
            return [int(x) for x in self._last_read.split(" ")]
        except:
            return []

    def on_single_value_update(self, mode: int, value: str) -> None:
        """BuildHat call this function when there is a device value update from a combo mode"""
        if mode == self._selected_read_mode:
            self._last_read = value
            if self._read_lock.locked():
                self._read_lock.release()
