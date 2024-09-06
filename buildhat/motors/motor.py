import asyncio

import buildhat.hat
from ..models.devicetype import DeviceType
from ..device import Device

_RAMP_DONE = ": ramp done"
_PULSE_DONE = ": pulse done"


class Motor(Device):
    def __init__(self, hat: buildhat.hat.Hat, port: str, type: DeviceType):
        super().__init__(hat, port, type)

        self._run_lock = asyncio.Lock()

    def _parse_ramp_done_message(self, line: str) -> bool:
        """Parse a line received from HAT and search for ramp done message.
        When the message is found, release the run lock
        """
        msg = f"P{self._port}{_RAMP_DONE}"
        if line.startswith(msg):
            self._run_lock.release()
            return True

        return False

    def _parse_pulse_done_message(self, line: str) -> bool:
        """Parse a line received from HAT and search for pulse done message.
        When the message is found, release the run lock
        """
        msg = f"P{self._port}{_PULSE_DONE}"
        if line.startswith(msg):
            self._run_lock.release()
            return True

        return False
