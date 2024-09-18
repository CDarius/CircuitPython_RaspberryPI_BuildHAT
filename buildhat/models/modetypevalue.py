# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

from .enumstr import EnumStr


class ModeTypeValue(EnumStr):
    """The type of value for a mode"""

    RAW = None
    PERCENT = None
    SIGNAL = None


ModeTypeValue.RAW = ModeTypeValue("Raw")
ModeTypeValue.PERCENT = ModeTypeValue("Percent")
ModeTypeValue.SIGNAL = ModeTypeValue("Signal")
