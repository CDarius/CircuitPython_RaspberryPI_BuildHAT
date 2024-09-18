# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

try:
    from typing import Self
except ImportError:
    pass


class EnumStr:
    def __init__(self, desciption: str):
        self._description = desciption

    def __str__(self) -> str:
        return self._description

    def __eq__(self, other):
        if isinstance(other, EnumStr):
            return self._description == other._description
        elif isinstance(other, str):
            return self._description == other
        else:
            return False

    def __hash__(self) -> int:
        return hash(self._description)

    @classmethod
    def parse(cls, value: str) -> Self | None:
        if not value or not isinstance(value, str):
            return None

        value = value.lower()

        for k, v in [(k, v) for k, v in cls.__dict__.items() if not k.startswith("_")]:
            if isinstance(v, cls):
                if v._description.lower() == value:
                    return v

        return None
