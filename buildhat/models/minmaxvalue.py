# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

from .modetypevalue import ModeTypeValue


class MinMaxValue:
    def __init__(self, type: ModeTypeValue, min: int, max: int):
        self._type = type
        self._min = min
        self._max = max

    @property
    def value_type(self) -> ModeTypeValue:
        return self._type

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max

    def __str__(self) -> str:
        return f"{{type={self._type}, min={self._min}, max={self._max}}}"
