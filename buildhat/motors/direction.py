# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

from ..models.enumstr import EnumStr


class Direction(EnumStr):
    """Motor turn mode"""

    """Shortest direction to reach the target"""
    SHORTEST = None
    """Clockwise"""
    CW = None
    """Counter clockwise"""
    CCW = None


Direction.SHORTEST = Direction("Shortest")
Direction.CW = Direction("Clockwise")
Direction.CCW = Direction("Counter clockwise")
