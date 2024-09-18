# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

"""
Test code for Lego® Technic 3x3 Color Light Matrix
Part number: 45608
"""

import asyncio

import board

from buildhat.devices.matrixcolor import MatrixColor
from buildhat.devices.matrixtransition import MatrixTransition
from buildhat.hat import Hat

matrix_port = 2

# Pins for Waveshare RP2040-Zero.
# Change the pins if you are using a different board
tx_pin = board.TX
rx_pin = board.RX
reset_pin = board.GP23

buildhat = Hat(tx=tx_pin, rx=rx_pin, reset=reset_pin, debug=True)

stop = False


async def buildhat_loop(hat):
    while not stop:
        hat.update()
        await asyncio.sleep(0)


async def matrix_loop(hat):
    while not stop:
        matrix = buildhat.get_device(matrix_port)

        matrix.display_single_color(MatrixColor.YELLOW)
        await asyncio.sleep(1)

        for i in range(10):
            matrix.display_level_bar(i)
            await asyncio.sleep(0.3)

        matrix.set_display_image_transition(MatrixTransition.SWIPE_RTL)
        matrix.display_single_color(MatrixColor.YELLOW)
        await asyncio.sleep(2)
        matrix.display_single_color(MatrixColor.BLUE)
        await asyncio.sleep(2)
        matrix.display_single_color(MatrixColor.RED)
        await asyncio.sleep(2)

        matrix.set_display_image_transition(MatrixTransition.FADE_IN_OUT)
        matrix.fill_pixels(MatrixColor.YELLOW, 5)
        matrix.set_pixel(1, 1, MatrixColor.BLUE, 10)
        matrix.display_pixels()
        await asyncio.sleep(2)
        matrix.fill_pixels(MatrixColor.YELLOW, 5)
        matrix.set_pixel(0, 0, MatrixColor.BLUE, 10)
        matrix.set_pixel(2, 2, MatrixColor.BLUE, 10)
        matrix.display_pixels()
        await asyncio.sleep(2)
        matrix.fill_pixels(MatrixColor.YELLOW, 5)
        matrix.set_pixel(0, 0, MatrixColor.BLUE, 10)
        matrix.set_pixel(1, 1, MatrixColor.BLUE, 10)
        matrix.set_pixel(2, 2, MatrixColor.BLUE, 10)
        matrix.display_pixels()
        await asyncio.sleep(2)
        matrix.set_display_image_transition(MatrixTransition.NONE)
        matrix.fill_pixels(MatrixColor.YELLOW, 5)
        matrix.set_pixel(0, 0, MatrixColor.BLUE, 10)
        matrix.set_pixel(0, 2, MatrixColor.BLUE, 10)
        matrix.set_pixel(2, 2, MatrixColor.BLUE, 10)
        matrix.set_pixel(2, 0, MatrixColor.BLUE, 10)
        matrix.display_pixels()
        await asyncio.sleep(2)


async def main():
    buildhat_loop_task = asyncio.create_task(buildhat_loop(buildhat))
    matrix_loop_task = asyncio.create_task(matrix_loop(buildhat))

    await asyncio.gather(buildhat_loop_task, matrix_loop_task)


asyncio.run(main())
