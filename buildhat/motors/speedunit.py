# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

from ..models.enumstr import EnumStr


class SpeedUnit(EnumStr):
    """Motor speed unit enum"""

    RPM = None
    """Revolution per minute"""

    DGS = None
    """Degree per seconds"""


SpeedUnit.RPM = SpeedUnit("RPM")
SpeedUnit.DGS = SpeedUnit("DGS")
