# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

from ..models.enumstr import EnumStr


class MatrixTransition(EnumStr):
    """3x3 matrix image transition enum like class"""

    def __init__(self, desciption: str, transition_num: int):
        super().__init__(desciption)
        self._transition_num = transition_num

    @property
    def transition_num(self) -> int:
        return self._transition_num

    NONE = None
    """No transition, immediate pixel drawing"""

    SWIPE_RTL = None
    """Right-to-left wipe in/out

    If the timing between writing new matrix pixels is less than one second
    the transition will clip columns of pixels from the right
    """

    FADE_IN_OUT = None
    """Fade-in/Fade-out

    The fade in and fade out take about 2.2 seconds for full fade effect.
    Waiting less time between setting new pixels will result in a faster
    fade which will cause the fade to "pop" in brightness
    """


MatrixTransition.NONE = MatrixTransition("No transition, immediate pixel drawing", 0)
MatrixTransition.SWIPE_RTL = MatrixTransition("Right-to-left wipe in/out", 1)
MatrixTransition.FADE_IN_OUT = MatrixTransition("Fade-in/Fade-out", 2)
