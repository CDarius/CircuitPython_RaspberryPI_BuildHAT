try:
    from typing import List
except:
    pass


class CombiModes:
    """A combi mode is a list of available modes"""

    def __init__(self, number: int, modes: List[int]):
        self._number = number
        self._modes = modes

    @property
    def number(self) -> int:
        """Combi number"""
        return self._number

    @property
    def modes(self) -> List[int]:
        """Combi modes list"""
        return self._modes

    def __str__(self) -> str:
        smodes = [f"M{x}" for x in self._modes]
        return f"{{num={self._number}, modes={smodes}}}"
