# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

from ..activedevice import ActiveDevice
from ..hatserialcomm import HatSerialCommunication
from ..models.devicetype import DeviceType
from .matrixcolor import MatrixColor
from .matrixtransition import MatrixTransition

try:
    from typing import List
except ImportError:
    pass


class LightMatrix(ActiveDevice):
    """3x3 light matrix

    Lego® part number: 45608

    .. image:: https://img.bricklink.com/ItemImage/SN/0/45608-1.png
        :width: 400
        :alt: 3x3 light matrix

    Image from `Bricklink <https://www.bricklink.com/v2/catalog/catalogitem.page?S=45608>`__

    """

    def __init__(self, hat: HatSerialCommunication, port: int, type: int):
        super().__init__(hat, port, type)

        self.on()
        self.select_read_mode(2)  # PIX O SI
        self._matrix_color: List[MatrixColor] = [MatrixColor.BLACK] * 9
        self._matrix_brightness: List[int] = [0] * 10

    def on(self):
        """Turn on the device"""
        self.hat.serial.write(f"port {self._port} ; plimit 1 ; set -1\r")

    def off(self):
        """Turn off the device"""

        # Never send the "off" command to the port a Matrix is connected to
        # Instead, just turn all the pixels off
        self.display_single_color(MatrixColor.BLACK)

    def display_single_color(self, color: MatrixColor) -> None:
        """Display the same color on all 9 pixels

        :param color: Color to display. Instance of MatrixColor
        :param brightness: Leds brightsness from 0 to 10
        """
        LightMatrix._validate_color(color)
        data = bytearray(2)
        data[0] = 0xC1
        data[1] = color.color_num
        self.select_read_mode(1)  # COL O
        self._write1(data)

    def display_level_bar(self, level: int) -> None:
        """Display a level bar from 0 to 9

        The level bar is always green

        :param level: The height of the bar. Range 0 to 9
        """
        level = max(0, min(9, level))
        data = bytearray(2)
        data[0] = 0xC0
        data[1] = level
        self.select_read_mode(0)  # LEV O
        self._write1(data)

    def set_pixel(self, x: int, y: int, color: MatrixColor, brightness: int) -> None:
        """Set color and brightness of one pixel in the buffer

        :param x: X pixel coordinate. 0 to 2
        :param y: Y pixel coordinate. 0 to 2
        :param color: Pixel color from `MatrixColor`
        :param brightness: Pixel brightness. 0 to 10

        .. important:: Pixel changes are not displayed. Use display_pixels to display the changes

        """
        if x < 0 or x > 2:
            raise ValueError("X coordinate must be in range 0 to 2")
        if y < 0 or y > 2:
            raise ValueError("Y coordinate must be in range 0 to 2")

        LightMatrix._validate_color(color)
        LightMatrix._validate_brightness(brightness)
        index = y * 3 + x
        self._matrix_color[index] = color
        self._matrix_brightness[index] = brightness

    def fill_pixels(self, color: MatrixColor, brightness: int) -> None:
        """Fill the pixels buffer with one color

        :param color: Pixel color from `MatrixColor`
        :param brightness: Pixel brightness. 0 to 10

        .. important:: Pixel changes are not displayed. Use display_pixels to display the changes

        """
        LightMatrix._validate_color(color)
        LightMatrix._validate_brightness(brightness)
        for i in range(9):
            self._matrix_color[i] = color
            self._matrix_brightness[i] = brightness

    def display_pixels(self) -> None:
        """Display the current pixels buffer"""
        data = bytearray(10)
        data[0] = 0xC2
        for i in range(9):
            data[i + 1] = (self._matrix_brightness[i] << 4) | self._matrix_color[i].color_num

        self.select_read_mode(2)  # PIX O SI
        self._write1(data)

    def set_display_image_transition(self, transition: MatrixTransition) -> None:
        """Set the transition mode between the images on the display

        :param transition: Desired transition. Instance of MatrixTransition

        Setting a new transition mode will wipe the screen and interrupt any
        running transition. See :py:class:`MatrixTransition<buildhat.devices.matrixtransition.MatrixTransition>`
        for the available options.

        """
        if not isinstance(transition, MatrixTransition):
            raise ValueError("Transition must be an instance of MatrixTransition")

        data = bytearray(2)
        data[0] = 0xC3
        data[1] = transition.transition_num
        self.select_read_mode(3)  # TRANS SI
        self._write1(data)
        self.select_read_mode(2)  # PIX O SI

    def _validate_color(color: MatrixColor) -> None:
        if not isinstance(color, MatrixColor):
            raise ValueError("Color should be an instance of MatrixColor")

    def _validate_brightness(brightness: int) -> None:
        if brightness < 0 or brightness > 10:
            raise ValueError("Brightness out of range. Allowed range 0 to 10")
