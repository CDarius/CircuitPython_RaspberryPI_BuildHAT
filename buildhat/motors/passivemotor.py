# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

from ..device import Device
from ..hatserialcomm import HatSerialCommunication
from ..models.devicetype import DeviceType
from .motor import Motor


class PassiveMotor(Motor):
    """A Lego® passive motor

    Passive motor are passive device threrefore can not return data to the hat. Passive motor have
    no encoder are simple DC motors

    .. image:: https://img.bricklink.com/ItemImage/SN/0/88011-1.png
        :width: 400
        :alt: Train motor

    `Train motor image from Bricklink <https://www.bricklink.com/v2/catalog/catalogitem.page?S=88011-1&name=Train%20Motor&category=%5BPower%20Functions%5D%5BPowered%20Up%5D#T=S&O={%22iconly%22:0}>`_
    """

    def __init__(self, hat: HatSerialCommunication, port: int, type: int):
        super().__init__(hat, port, type)
        Motor.__init__(self, hat, port, type)

        self.stop()

        self.default_speed = 0.3
        self._speed = 0

        # Set full power on motor
        self.power_limit = 1.0

    @property
    def power_limit(self) -> float:
        """Motor power limit. Range 0 to 1

        :raises ValueError: Occurs if invalid power limit passed
        """
        return self._power_limit

    @power_limit.setter
    def power_limit(self, limit: float) -> None:
        limit = float(limit)
        if not (limit >= 0 and limit <= 1):
            raise ValueError("Power limit should be in range 0 to 1")
        self.hat.serial.write(f"port {self.port} ; port_plimit {limit}\r")
        self._power_limit = limit

    @property
    def default_speed(self) -> float:
        """Set the default speed of the motor. Range -1 to 1

        :raises ValueError: Occurs if invalid speed passed
        """
        return self._default_speed

    @default_speed.setter
    def default_speed(self, speed: float) -> None:
        speed = float(speed)
        if not (speed >= 0 and speed <= 1):
            raise ValueError("Speed should be in range -1 to 1")
        self._default_speed = speed

    @property
    def actual_speed(self) -> float:
        """Motor actaul speed in range -1 to 1."""
        return self._actual_speed

    def pwmparams(self, pwmthresh, minpwm):
        """PWM thresholds

        :param pwmthresh: Value 0 to 1, threshold below, will switch from fast to slow, PWM
        :param minpwm: Value 0 to 1, threshold below which it switches off the drive altogether
        :raises ValueError: Occurs if invalid values are passed
        """
        if not (pwmthresh >= 0 and pwmthresh <= 1):
            raise ValueError("pwmthresh should be 0 to 1")
        if not (minpwm >= 0 and minpwm <= 1):
            raise ValueError("minpwm should be 0 to 1")
        self.hat.serial.write(f"port {self.port} ; pwmparams {pwmthresh} {minpwm}\r")

    def start(self, speed: float | None = None) -> None:
        """Start motor

        :param speed: Speed ranging from -1 to 1 or default_speed if None
        :raises ValueError: Occurs if invalid speed passed or motor is not connected anymore

        Example code:

        .. code-block:: python

            import board
            import asyncio
            from buildhat.hat import Hat

            motor_port = 0
            buildhat = Hat(tx=board.TX, rx=board.RX, reset=board.GP23, debug=True)

            async def buildhat_loop(hat):
                while True:
                    hat.update()
                    await asyncio.sleep(0)

            async def motor_loop(hat):
                motor = buildhat.get_device(motor_port)
                while True:
                    print('Start the motor')
                    motor.start()
                    await asyncio.sleep(2)

                    print('Stop the motor')
                    motor.stop()
                    await asyncio.sleep(1)

            async def main():
                buildhat_loop_task = asyncio.create_task(buildhat_loop(buildhat))
                motor_loop_task = asyncio.create_task(motor_loop(buildhat))

                await asyncio.gather(buildhat_loop_task, motor_loop_task)

            asyncio.run(main())

        """
        self.ensure_connected()

        if self._actual_speed == speed:
            # Already running at this speed, do nothing
            return

        if speed is None:
            speed = self._default_speed
        elif not (-1 <= speed <= 1):
            raise ValueError("Speed should be in range -1 to 1")
        self.hat.serial.write(f"port {self._port} ; pwm ; set {speed}\r")
        self._actual_speed = speed

    async def run_for_seconds(self, seconds: float, speed: float | None = None, blocking: bool = True) -> None:
        """Start motor

        :param seconds: Running time in seconds
        :param speed: Speed ranging from -1 to 1 or default_speed if None
        :param blocking: Whether call should block till finished
        :raises ValueError: Occurs if invalid speed passed or motor is not connected anymore

        Example code:

        .. code-block:: python

            import board
            import asyncio
            from buildhat.hat import Hat

            motor_port = 0
            buildhat = Hat(tx=board.TX, rx=board.RX, reset=board.GP23, debug=True)

            async def buildhat_loop(hat):
                while True:
                    hat.update()
                    await asyncio.sleep(0)

            async def motor_loop(hat):
                motor = buildhat.get_device(motor_port)
                while True:
                    print("Motor running")
                    await motor.run_for_seconds(2)
                    print("Motor running done")

                    await asyncio.sleep(1)

            async def main():
                buildhat_loop_task = asyncio.create_task(buildhat_loop(buildhat))
                motor_loop_task = asyncio.create_task(motor_loop(buildhat))

                await asyncio.gather(buildhat_loop_task, motor_loop_task)

            asyncio.run(main())
        """
        self.ensure_connected()

        if self._actual_speed == speed:
            # Already running at this speed, do nothing
            return

        if speed is None:
            speed = self._default_speed
        elif not (-1 <= speed <= 1):
            raise ValueError("Speed should be in range -1 to 1")
        self.hat.serial.write(f"port {self._port} ; pwm ; set pulse {speed} 0.0 {seconds} 0\r")
        self._actual_speed = speed

        if blocking:
            await self._run_lock.acquire()
            self.hat.push_device_message_handle(self, self._parse_pulse_done_message)
            # Wait for the lock to be released by _parse_ramp_done_message
            async with self._run_lock:
                pass
            if not self._is_connected:
                raise Exception("Motor is not anymore connected")

    def stop(self) -> None:
        """Stop motor"""
        self.hat.serial.write(f"port {self.port} ; off\r")
        self._actual_speed = 0

    def on(self):
        """Start the motor at the maximum speed"""
        self.start(speed=1)

    def off(self):
        """Stop motor"""
        self.stop()
