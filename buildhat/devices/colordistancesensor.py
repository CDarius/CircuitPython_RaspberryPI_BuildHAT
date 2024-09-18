# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

import asyncio

from ..activedevice import ActiveDevice
from ..hatserialcomm import HatSerialCommunication
from ..models.devicetype import DeviceType
from .color import Color

try:
    from typing import List, Tuple
except ImportError:
    pass


class ColorDistanceSensor(ActiveDevice):
    """Boost color & distance sensor

    Lego® part number: 88007

    .. image:: https://img.bricklink.com/ItemImage/SN/0/88007-1.png
        :width: 400
        :alt: Color & distance sensor

    Image from `Bricklink <https://www.bricklink.com/v2/catalog/catalogitem.page?S=88007>`__

    """

    def __init__(self, hat: HatSerialCommunication, port: int, type: int):
        super().__init__(hat, port, type)

        self._read_lock = asyncio.Lock()

        self.num_read_average = 4
        self.off()

    @property
    def num_read_average(self) -> int:
        """Number of reads to compute the average result. Range 1 to 25

        The value of this property is used to calculate the average in the following methods:

            * `get_color`
            * `get_color_rgb`
            * `get_ambient_light`
            * `get_reflected_light`

        .. tip:: Setting this property value to 1 disable the average calculation

        """
        return self._num_read_average

    @num_read_average.setter
    def num_read_average(self, num: int) -> None:
        if 1 <= num <= 25:
            self._num_read_average = num
        else:
            raise ValueError("Parameter num should be in range 1-25")

    def off(self) -> None:
        """Turn off the device"""
        self.set_color(Color.BLACK)

    async def get_color(self) -> Color:
        """Read the color and return the nearest Lego® color

        It takes `num_read_average` reads to compute the average color value
        """
        r, g, b = await self.get_color_rgb()
        return Color.get_color_from_rgb(r, g, b)

    async def get_color_rgb(self) -> Tuple[int, int, int]:
        """Read the color in RGB format

        It takes `num_read_average` reads to compute the average color value
        """
        self.ensure_connected()
        self.select_read_mode(6)  # RGB I

        reads = []
        while len(reads) < self._num_read_average:
            update = await self._wait_for_one_update()
            if len(update) == 3:
                reads.append(update)
        return self._avgrgb(reads)

    def _clamp(self, val, small, large):
        return max(small, min(val, large))

    def _avgrgb(self, reads: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
        readings = []
        for read in reads:
            readings.append(
                [
                    int((self._clamp(read[0], 0, 400) / 400) * 255),
                    int((self._clamp(read[1], 0, 400) / 400) * 255),
                    int((self._clamp(read[2], 0, 400) / 400) * 255),
                ]
            )
        rgb = []
        for i in range(3):
            rgb.append(int(sum([rgb[i] for rgb in readings]) / len(readings)))
        return rgb

    async def get_ambient_light(self) -> int:
        """Read the intensity of the  ambient light. Range 0 to 100

        It takes `num_read_average` reads to compute the average color value
        """
        self.ensure_connected()
        self.select_read_mode(4)  # AMBI

        reads = []
        while len(reads) < self._num_read_average:
            update = await self._wait_for_one_update()
            if len(update) == 1:
                reads.append(update[0])

        return int(sum(reads) / self._num_read_average)

    async def get_reflected_light(self) -> int:
        """Read the intensity of reflected light. Range 0 to 100

        It takes `num_read_average` reads to compute the average color value
        """
        self.ensure_connected()
        self.select_read_mode(3)  # REFLT

        reads = []
        while len(reads) < self._num_read_average:
            update = await self._wait_for_one_update()
            if len(update) == 1:
                reads.append(update[0])

        return int(sum(reads) / self._num_read_average)

    async def get_distance(self) -> int:
        """Read the distance from an obstacle in range 0-10"""
        self.ensure_connected()
        self.select_read_mode(1)  # PROX

        return (await self._wait_for_one_update())[0]

    async def get_counter(self) -> int:
        """Return the counted object"""
        self.ensure_connected()
        self.select_read_mode(2)  # COUNT

        return (await self._wait_for_one_update())[0]

    def set_color(self, color: Color) -> None:
        """Set the led color. No measures performed in this mode

        :param color: Color to display
        """
        self.ensure_connected()
        self.select_read_mode(5)  # COL O

        color_num = 0  # black
        if color in (Color.BLUE, Color.CYAN):
            color_num = 3  # blue
        elif color in (Color.RED, Color.VIOLET, Color.YELLOW):
            color_num = 9  # red
        elif color == Color.GREEN:
            color_num = 5  # green
        elif color == Color.WHITE:
            color_num = 10  # all rgb led

        data = bytearray(2)
        data[0] = 0xC5
        data[1] = color_num
        self._write1(data)

    async def _wait_for_one_update(self) -> List[int]:
        await self._read_lock.acquire()
        # Wait for the lock to be released on next update in on_single_value_update
        async with self._read_lock:
            pass
        try:
            return [int(x) for x in self._last_read.split(" ")]
        except Exception:
            return []

    def on_single_value_update(self, mode: int, value: str) -> None:
        """BuildHat call this function when there is a device value update from a combo mode"""
        if mode == self._selected_read_mode:
            self._last_read = value
            if self._read_lock.locked():
                self._read_lock.release()
