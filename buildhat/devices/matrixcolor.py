from ..models.enumstr import EnumStr


class MatrixColor(EnumStr):
    """3x3 matrix led color"""

    def __init__(self, desciption: str, color_num: int):
        super().__init__(desciption)
        self._color_num = color_num

    @property
    def color_num(self) -> int:
        return self._color_num

    BLACK = None
    BROWN = None
    MAGENTA = None
    BLUE = None
    CYAN = None
    PALE_GREEN = None
    GREEN = None
    YELLOW = None
    ORANGE = None
    RED = None
    WHITE = None


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
