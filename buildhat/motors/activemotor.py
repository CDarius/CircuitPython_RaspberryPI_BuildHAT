import asyncio

import buildhat.hat
from ..models.devicetype import DeviceType
from .speedunit import SpeedUnit
from .direction import Direction
from ..activedevice import ActiveDevice
from .motor import Motor

try:
    from typing import List, Tuple
except:
    pass


class ActiveMotor(ActiveDevice, Motor):
    def __init__(self, hat: buildhat.hat.Hat, port: str, type: DeviceType):
        super().__init__(hat, port, type)
        Motor.__init__(self, hat, port, type)

        self.off()

        # Default power limit is 0.1, too low
        self.power_limit = 0.7

        self._actual_speed = 0
        self._actual_position = 0
        self._actual_absolute_position = 0
        self._has_absolute_position = "APOS" in [m.name for m in self._mode_details]

        self._position_offset = 0
        self.reverse_direction = False

        self.run_command_speed_unit = SpeedUnit.RPM
        self.run_command_default_speed = 240.0
        self.run_command_position_tolerance = 5
        self.release_after_run = True

        self.set_speed_pid(p=0, i=2.5, d=0.0)
        self.set_position_pid(p=5, i=0, d=0.1)

        # Select the first combi mode
        if self._combi_modes:
            self.select_read_mode(self._combi_modes[0])

    def deinit(self) -> None:
        super().deinit()
        self._run_lock.release()

    @property
    def power_limit(self) -> float:
        """Motor power limit. Range 0 to 1"""
        return self._power_limit

    @power_limit.setter
    def power_limit(self, limit: float) -> None:
        if not (limit >= 0 and limit <= 1):
            raise ValueError("Power limit should be in range 0 to 1")
        self.hat.serial.write(f"port {self.port} ; port_plimit {limit}\r")
        self._power_limit = limit

    @property
    def actual_speed(self) -> int:
        """Get motor actual speed in degrees/sec"""
        return self._actual_speed * self._reverse_direction_factor

    @property
    def actual_position(self) -> int:
        """Position of motor in degress"""
        return (
            self._actual_position + self._position_offset
        ) * self._reverse_direction_factor

    @actual_position.setter
    def actual_position(self, new_position) -> None:
        self._position_offset = (
            int(new_position / self._reverse_direction_factor) - self._actual_position
        )

    @property
    def actual_absolute_position(self) -> int:
        """Get absolute position of motor in degrees from -180 to 180"""
        if not self._has_absolute_position:
            raise Exception("This motor do not provide absolute position")

        return self._actual_absolute_position * self._reverse_direction_factor

    @property
    def has_absolute_position(self) -> bool:
        """Motor can provide abosuole position"""
        return self._has_absolute_position

    @property
    def reverse_direction(self) -> bool:
        """Reverse motor rotation direction and position counting direction"""
        return self._reverse_direction_factor == -1

    @reverse_direction.setter
    def reverse_direction(self, reverse: bool) -> None:
        self._reverse_direction_factor = -1 if reverse else 1

    @property
    def run_command_speed_unit(self) -> SpeedUnit:
        """Speed unit used when the motor is commanded to run"""
        return self._run_speed_unit

    @run_command_speed_unit.setter
    def run_command_speed_unit(self, unit: SpeedUnit) -> None:
        if not isinstance(unit, SpeedUnit):
            raise ValueError("Illegal unit parameter. It must be a SpeedUnit")

        self._run_speed_unit = unit

    @property
    def run_command_default_speed(self) -> float:
        """Default speed used when no speed is provided on a run command"""
        return self._run_default_speed

    @run_command_default_speed.setter
    def run_command_default_speed(self, value: float) -> None:
        self._run_default_speed = float(value)

    @property
    def run_command_position_tolerance(self) -> int:
        """Position tolerance in degrees for a run command"""
        return self._run_position_tolerance

    @run_command_position_tolerance.setter
    def run_command_position_tolerance(self, value: int) -> None:
        self._run_position_tolerance = int(value)

    @property
    def speed_pid(self) -> Tuple[float, float, float]:
        """Return speed PID proportional, integral and derivative factors when speed is greater than low_speed_pid_threshold_rpm"""
        return self._speed_pid_value

    def set_speed_pid(self, p: float = 0, i: float = 0, d: float = 0) -> None:
        self._speed_pid_value = (p, i, d)

    @property
    def position_pid(self) -> Tuple[float, float, float]:
        """Return position PID proportional, integral and derivative factors"""
        return self._position_pid_value

    def set_position_pid(self, p: float = 0, i: float = 0, d: float = 0) -> None:
        self._position_pid_value = (p, i, d)

    @property
    def release_after_run(self) -> bool:
        """Determine if motor is released after running, so can be turned by hand"""
        return self._release_after_run

    @release_after_run.setter
    def release_after_run(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("Must pass boolean")
        self._release_after_run = value

    async def run_for_rotations(
        self, rotations: int | float, speed: float | None = None, blocking: bool = True
    ):
        """Run motor for N rotations

        :param rotations: Number of rotations
        :param speed: Speed in run_command_speed_unit
        :param blocking: Whether call should block till finished
        :raises ValueError: Occurs if invalid speed passed
        """
        await self.run_for_degrees(
            degrees=int(rotations * 360), speed=speed, blocking=blocking
        )

    async def run_for_degrees(
        self, degrees: int | float, speed: float | None = None, blocking: bool = True
    ):
        """Run motor for N degrees

        :param degrees: Number of degrees to rotate
        :param speed: Speed in run_command_speed_unit
        :param blocking: Whether call should block till finished
        :raises ValueError: Occurs if invalid speed passed
        """
        if speed is None:
            speed = self._run_default_speed

        degrees *= self._reverse_direction_factor

        mul = 1
        if speed < 0:
            speed = abs(speed)
            mul = -1
        pos = self._actual_position
        newpos = ((degrees * mul) + pos) / 360.0
        pos /= 360.0
        await self._run_positional_ramp(pos, newpos, speed, blocking)

    async def run_to_position(
        self,
        target_position: int | float,
        speed: float | None = None,
        blocking: bool = True,
    ):
        """Run motor until reach the target position

        :param target_position: Position to reach in degrees
        :param speed: Speed in run_command_speed_unit
        :param blocking: Whether call should block till finished
        :raises ValueError: Occurs if invalid speed passed
        """
        if speed is None:
            speed = self._run_default_speed

        target_position = (
            target_position * self._reverse_direction_factor - self._position_offset
        )

        mul = 1
        if speed < 0:
            speed = abs(speed)
            mul = -1
        pos = self._actual_position
        newpos = target_position * mul / 360.0
        pos /= 360.0
        await self._run_positional_ramp(pos, newpos, speed, blocking)

    async def _run_positional_ramp(
        self, pos: float, newpos: float, speed: float, blocking: bool
    ):
        """Ramp motor

        :param pos: Current motor position in decimal rotations (from preset position)
        :param newpos: New motor postion in decimal rotations (from preset position)
        :param speed: Speed in run_command_speed_unit
        """
        self.ensure_connected()

        # Test that no other locking running command are in progress
        async with self._run_lock:
            pass

        speed = self._normalize_speed(speed)
        dur = abs((newpos - pos) / speed)
        kp, ki, kd = self._position_pid_value
        self.hat.serial.write(
            f"port {self.port}; select 0 ; selrate {self._data_update_interval}; "
        )
        # scale unwap kp ki kd windup deadzone
        self.hat.serial.write(
            f"pid {self.port} 0 1 s4 0.0027777778 0 {kp} {ki} {kd} 3 0.001; "
        )
        self.hat.serial.write(f"set ramp {pos} {newpos} {dur} 0\r")

        if blocking:
            await self._run_lock.acquire()
            self.hat.push_device_message_handle(self, self._parse_ramp_done_message)
            # Wait for the lock to be released by _parse_ramp_done_message
            async with self._run_lock:
                pass
            if not self._is_connected:
                raise Exception("Motor is not anymore connected")

            # Restart the PID if the position tollerance has not been reached
            newpos_deg = int(newpos * 360.0)
            if abs(newpos_deg - self._actual_position) > self._run_position_tolerance:
                self._run_positional_ramp(self._actual_position / 360, newpos, speed, blocking)

            if self._release_after_run:
                self.coast()

    def _normalize_speed(self, speed_value: float) -> float:
        """Transform the speed from user select unit to revolutions per seconds"""
        if self._run_speed_unit == SpeedUnit.RPM:
            return speed_value / 60.0
        elif self._run_speed_unit == SpeedUnit.DGS:
            return speed_value / 360.0

    def _get_speed_in_rpm(self, speed_value: float) -> float:
        """Transform the speed from user select unit to revolutions per seconds"""
        if self._run_speed_unit == SpeedUnit.RPM:
            return speed_value
        elif self._run_speed_unit == SpeedUnit.DGS:
            return speed_value / 60.0

    def _get_speed_in_dgs(self, speed_value: float) -> float:
        """Transform the speed from user select unit to revolutions per seconds"""
        if self._run_speed_unit == SpeedUnit.RPM:
            return speed_value * 60.0
        elif self._run_speed_unit == SpeedUnit.DGS:
            return speed_value

    async def run_to_absolute_angle(
        self,
        angle: int,
        speed: float | None = None,
        blocking: bool = True,
        direction: Direction = Direction.SHORTEST,
    ):
        """Run motor to an absolute angle

        :param angle: Position in degrees from -180 to 180
        :param speed: Speed ranging from 0 to 100
        :param blocking: Whether call should block till finished
        :param direction: shortest (default)/clockwise/anticlockwise
        :raises ValueError: Occurs if invalid angle passed
        """
        self.ensure_connected()

        if speed is None:
            speed = self._run_default_speed

        if angle < -180 or angle > 180:
            raise ValueError("Invalid angle. Allower range [-180,180]")

        pos = self._actual_position
        if self._has_absolute_position:
            apos = self._actual_absolute_position
        else:
            apos = pos
        diff = (angle - apos + 180) % 360 - 180
        newpos = (pos + diff) / 360
        v1 = (angle - apos) % 360
        v2 = (apos - angle) % 360
        mul = 1
        if diff > 0:
            mul = -1
        diff = sorted([diff, mul * (v2 if abs(diff) == v1 else v1)])
        if direction == Direction.SHORTEST:
            pass
        elif direction == Direction.CW:
            newpos = (pos + diff[1]) / 360
        elif direction == Direction.CCW:
            newpos = (pos + diff[0]) / 360
        else:
            raise ValueError("Invalid direction, should be Direction value")

        # Convert current motor position to decimal rotations from preset position to match newpos units
        pos /= 360.0
        await self._run_positional_ramp(
            pos=pos, newpos=newpos, speed=speed, blocking=blocking
        )

    async def run_for_seconds(
        self, seconds: float, speed: float | None = None, blocking: bool = True
    ):
        """Run motor for N seconds

        :param seconds: Running time in seconds
        :param speed: Speed in run_command_speed_unit
        :param blocking: Whether call should block till finished
        """
        self.ensure_connected()

        # Test that no other locking running command are in progress
        async with self._run_lock:
            pass

        if speed is None:
            speed = self._run_default_speed

        speed *= self._reverse_direction_factor
        speed = self._normalize_speed(speed)
        kp, ki, kd = self._speed_pid_value
        if self._has_absolute_position:
            # scale unwap kp ki kd windup deadzone
            pid = f"pid_diff {self.port} 0 5 s2 0.0027777778 1 {kp} {ki} {kd} .4 0.01"
        else:
            # change speed unit to deca degrees/second
            speed *=36
            # scale unwap kp ki kd windup deadzone
            pid = f"pid {self.port} 0 0 s1 1 0 0.003 0.01 0 100 0.01"
        cmd = f"port {self.port} ; select 0 ; selrate {self._data_update_interval}; {pid} ; set pulse {speed} 0.0 {seconds} 0\r"
        self.hat.serial.write(cmd)

        if blocking:
            await self._run_lock.acquire()
            self.hat.push_device_message_handle(self, self._parse_pulse_done_message)
            # Wait for the lock to be released by _parse_pulse_done_message
            async with self._run_lock:
                pass
            if not self._is_connected:
                raise Exception("Motor is not anymore connected")

            if self._release_after_run:
                self.coast()

    def start(self, speed: float | None = None):
        """Start motor

        :param speed: Speed in run_command_speed_unit
        """
        if speed is None:
            speed = self._run_default_speed

        speed *= self._reverse_direction_factor
        speed = self._normalize_speed(speed)
        kp, ki, kd = self._speed_pid_value
        if self._has_absolute_position:
            # scale unwap kp ki kd windup deadzone
            pid = f"pid_diff {self.port} 0 5 s2 0.0027777778 1 {kp} {ki} {kd} .4 0.01"
        else:
            # change speed unit to deca degrees/second
            speed *=36
            # scale unwap kp ki kd windup deadzone
            pid = f"pid {self.port} 0 0 s1 1 0 0.003 0.01 0 100 0.01"
        cmd = f"port {self.port} ; select 0 ; selrate {self._data_update_interval}; {pid} ; set {speed}\r"
        self.hat.serial.write(cmd)

    def stop(self):
        """Stop motor"""
        self.coast()

    def off(self):
        """Turn off the device"""
        self.pwm(0)

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
        self.hat.serial.write(f"port {self._port} ; pwmparams {pwmthresh} {minpwm}\r")

    def pwm(self, speed: int | float) -> None:
        if (
            (not isinstance(speed, int) and not isinstance(speed, float))
            or speed < -1
            or speed > 1
        ):
            raise ValueError("Speed must be a number between -1 and 1")
        self.hat.serial.write(f"port {self._port} ; pwm ; set {speed}\r")

    def coast(self):
        """Coast motor"""
        self.hat.serial.write(f"port {self._port} ; coast\r")

    def float(self):
        """Float motor"""
        self.pwm(0)

    def on_combi_value_update(self, combi_num: int, values: List[str]) -> None:
        """BuildHat call this function when there is a device value update from a combo mode"""
        updates = self._decode_combi_update(combi_num, values)
        if updates:
            for mode, value in updates.items():
                if mode.name == "SPEED":
                    self._actual_speed = int(value) * 10
                elif mode.name == "POS":
                    self._actual_position = int(value)
                elif mode.name == "APOS":
                    self._actual_absolute_position = int(value)
