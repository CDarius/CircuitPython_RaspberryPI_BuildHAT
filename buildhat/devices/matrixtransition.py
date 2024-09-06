from ..models.enumstr import EnumStr


class MatrixTransition(EnumStr):
    """3x3 matrix image transition"""

    def __init__(self, desciption: str, transition_num: int):
        super().__init__(desciption)
        self._transition_num = transition_num

    @property
    def transition_num(self) -> int:
        return self._transition_num

    NONE = None
    SWIPE_RTL = None
    FADE_IN_OUT = None


MatrixTransition.NONE = MatrixTransition("No transition, immediate pixel drawing", 0)
MatrixTransition.SWIPE_RTL = MatrixTransition("Right-to-left wipe in/out", 1)
MatrixTransition.FADE_IN_OUT = MatrixTransition("Fade-in/Fade-out", 2)
