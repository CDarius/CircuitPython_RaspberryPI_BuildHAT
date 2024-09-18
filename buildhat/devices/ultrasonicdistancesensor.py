# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

from ..activedevice import ActiveDevice
from ..hatserialcomm import HatSerialCommunication
from ..models.devicetype import DeviceType


class UltrasonicDistanceSensor(ActiveDevice):
    """Distance sensor

    Lego® part number: 6302968

    .. image:: https://img.bricklink.com/ItemImage/PN/11/37316c01.png
        :width: 400
        :alt: Color & distance sensor

    Image from `Bricklink <https://www.bricklink.com/v2/catalog/catalogitem.page?P=37316c01>`__
    """

    def __init__(self, hat: HatSerialCommunication, port: int, type: int):
        super().__init__(hat, port, type)
        self._distance = -1
        self.on()
        self.select_read_mode(0)

    def on(self):
        """Turn on the device"""
        self.hat.serial.write(f"port {self.port} ; set -1\r")

    @property
    def distance(self) -> int:
        """Return the distance in mm

        .. code-block:: python

            import board
            import asyncio
            from buildhat.hat import Hat

            sensor_port = 0
            buildhat = Hat(tx=board.TX, rx=board.RX, reset=board.GP23)

            async def buildhat_loop(hat):
                while True:
                    hat.update()
                    await asyncio.sleep(0)

            async def read_loop(hat):
                sensor = buildhat.get_device(sensor_port)

                while True:
                    d = sensor.distance
                    if d > 0:
                        print(f"Distance {d} mm")
                    else:
                        print("Please put an obstacle in front of the ultrasonic sensor")
                    await asyncio.sleep(0.2)

            async def main():
                buildhat_loop_task = asyncio.create_task(buildhat_loop(buildhat))
                read_loop_task = asyncio.create_task(read_loop(buildhat))

                await asyncio.gather(buildhat_loop_task, read_loop_task)

            asyncio.run(main())

        """
        return self._distance

    def eyes(self, *args: int) -> None:
        """
        Brightness of LEDs on sensor

        :param args: One or four brightness arguments of 0 to 100
        :raises DistanceSensorError: Occurs if invalid brightness passed

        If len(args) == 1 all led are set to the same brightness value
        If len(args) == 4 leds are set in this order: upper right, upper left, lower right, lower left

        .. code-block:: python

            import board
            import asyncio
            from buildhat.hat import Hat

            sensor_port = 0
            buildhat = Hat(tx=board.TX, rx=board.RX, reset=board.GP23)

            async def buildhat_loop(hat):
                while True:
                    hat.update()
                    await asyncio.sleep(0)

            async def eyes_loop(hat):
                sensor = buildhat.get_device(sensor_port)
                pause = 0.02

                while True:
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
                eyes_loop_task = asyncio.create_task(eyes_loop(buildhat))

                await asyncio.gather(buildhat_loop_task, eyes_loop_task)

            asyncio.run(main())

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
