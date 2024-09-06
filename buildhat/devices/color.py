import math
from ..models.enumstr import EnumStr

try:
    from typing import Self, Tuple
except ImportError:
    pass


class Color(EnumStr):
    """Lego color"""

    def __init__(self, desciption: str, r: int, g: int, b: int):
        super().__init__(desciption)
        self._rgb = (r, g, b)

    @property
    def rgb(self) -> Tuple[int, int, int]:
        return self._rgb

    BLACK = None
    VIOLET = None
    BLUE = None
    CYAN = None
    GREEN = None
    YELLOW = None
    RED = None
    WHITE = None

    def get_color_from_rgb(r: int, g: int, b: int) -> Self:
        """Return the color from RGB

        :param r: Red
        :param g: Green
        :param b: Blue
        :return: Name of the color as a string
        :rtype: str
        """
        table = [
            (Color.BLACK, Color.BLACK.rgb),
            (Color.VIOLET, Color.VIOLET.rgb),
            (Color.BLUE, Color.BLUE.rgb),
            (Color.CYAN, Color.CYAN.rgb),
            (Color.GREEN, Color.GREEN.rgb),
            (Color.YELLOW, Color.YELLOW.rgb),
            (Color.RED, Color.RED.rgb),
            (Color.WHITE, Color.WHITE.rgb),
        ]
        near = ""
        euc = 1.0e99999  # Infinite
        for itm in table:
            cur = math.sqrt(
                (r - itm[1][0]) ** 2 + (g - itm[1][1]) ** 2 + (b - itm[1][2]) ** 2
            )
            if cur < euc:
                near = itm[0]
                euc = cur
        return near


Color.BLACK = Color("black", 0, 0, 0)
Color.VIOLET = Color("violet", 127, 0, 255)
Color.BLUE = Color("blue", 0, 0, 255)
Color.CYAN = Color("cyan", 0, 183, 235)
Color.GREEN = Color("green", 0, 128, 0)
Color.YELLOW = Color("yellow", 255, 255, 0)
Color.RED = Color("red", 255, 0, 0)
Color.WHITE = Color("white", 255, 255, 255)
