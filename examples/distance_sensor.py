# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

"""
Test code for Lego® Technic Distance Sensor
Part number: 6302968
"""

import asyncio

import board

from buildhat.hat import Hat

sensor_port = 0

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


async def read_loop(hat):
    sensor = buildhat.get_device(sensor_port)

    while not stop:
        d = sensor.distance
        if d > 0:
            print(f"Distance {d} mm")
        else:
            print("Please put an obstacle in front of the ultrasonic sensor")
        await asyncio.sleep(0.2)


async def eyes_loop(hat):
    sensor = buildhat.get_device(sensor_port)
    pause = 0.02

    while not stop:
        # Drive all four eyes together
        for i in range(100):
            sensor.eyes(i)
            await asyncio.sleep(pause)

        # Drive all four eyes one a the time
        for i in range(100):
            sensor.eyes(i, 0, 0, 0)
            await asyncio.sleep(pause)
        for i in range(100):
            sensor.eyes(0, i, 0, 0)
            await asyncio.sleep(pause)
        for i in range(100):
            sensor.eyes(0, 0, i, 0)
            await asyncio.sleep(pause)
        for i in range(100):
            sensor.eyes(0, 0, 0, i)
            await asyncio.sleep(pause)


async def main():
    buildhat_loop_task = asyncio.create_task(buildhat_loop(buildhat))
    read_loop_task = asyncio.create_task(read_loop(buildhat))
    eyes_loop_task = asyncio.create_task(eyes_loop(buildhat))

    await asyncio.gather(buildhat_loop_task, read_loop_task, eyes_loop_task)


asyncio.run(main())
