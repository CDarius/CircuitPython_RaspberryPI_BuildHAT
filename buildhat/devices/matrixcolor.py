# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

from ..models.enumstr import EnumStr


class MatrixColor(EnumStr):
    """3x3 matrix led color enum like clas"""

    def __init__(self, desciption: str, color_num: int):
        super().__init__(desciption)
        self._color_num = color_num

    @property
    def color_num(self) -> int:
        return self._color_num

    BLACK = None
    """Black color"""

    BROWN = None
    """Brown color"""

    MAGENTA = None
    """Magenta color"""

    BLUE = None
    """Blue color"""

    CYAN = None
    """Cyan color"""

    PALE_GREEN = None
    """Pale green color"""

    GREEN = None
    """Green color"""

    YELLOW = None
    """Yellow color"""

    ORANGE = None
    """Orange color"""

    RED = None
    """Red color"""

    WHITE = None
    """White color"""


MatrixColor.BLACK = MatrixColor("black", 0)
MatrixColor.BROWN = MatrixColor("Brown", 1)
MatrixColor.MAGENTA = MatrixColor("Magenta", 2)
MatrixColor.BLUE = MatrixColor("Blue", 3)
MatrixColor.CYAN = MatrixColor("Cyan", 4)
MatrixColor.PALE_GREEN = MatrixColor("Pale green", 5)
MatrixColor.GREEN = MatrixColor("Green", 6)
MatrixColor.YELLOW = MatrixColor("Yellow", 7)
MatrixColor.ORANGE = MatrixColor("Orange", 8)
MatrixColor.RED = MatrixColor("Red", 9)
MatrixColor.WHITE = MatrixColor("White", 10)
