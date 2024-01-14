from materialyoucolor.utils.color_utils import lstar_from_argb, lstar_from_y
from materialyoucolor.hct.viewing_conditions import ViewingConditions
from materialyoucolor.hct.cam16 import Cam16
from materialyoucolor.hct.hct_solver import HctSolver
from materialyoucolor.utils.color_utils import rgba_from_argb


class Hct:
    def __init__(self, argb: int):
        cam = Cam16.from_int(argb)
        self.internal_hue = cam.hue
        self.internal_chroma = cam.chroma
        self.internal_tone = lstar_from_argb(argb)
        self.argb = argb

    def set_internal_state(self, argb: int):
        cam = Cam16.from_int(argb)
        self.internal_hue = cam.hue
        self.internal_chroma = cam.chroma
        self.internal_tone = lstar_from_argb(argb)
        self.argb = argb

    @staticmethod
    def from_hct(hue: float, chroma: float, tone: float):
        return Hct(int(HctSolver.solve_to_int(hue, chroma, tone)))

    @staticmethod
    def from_int(argb: int):
        return Hct(argb)

    def to_int(self) -> int:
        return self.argb

    def to_rgba(self) -> list:
        return rgba_from_argb(self.argb)

    @property
    def hue(self) -> float:
        return self.internal_hue

    @hue.setter
    def hue(self, new_hue: float):
        self.set_internal_state(
            int(
                HctSolver.solve_to_int(
                    new_hue, self.internal_chroma, self.internal_tone
                )
            )
        )

    @property
    def chroma(self) -> float:
        return self.internal_chroma

    @chroma.setter
    def chroma(self, new_chroma: float):
        self.set_internal_state(
            HctSolver.solve_to_int(self.internal_hue, new_chroma, self.internal_tone)
        )

    @property
    def tone(self) -> float:
        return self.internal_tone

    @tone.setter
    def tone(self, new_tone: float):
        self.set_internal_state(
            int(
                HctSolver.solve_to_int(
                    self.internal_hue, self.internal_chroma, new_tone
                )
            )
        )

    def in_viewing_conditions(self, vc: ViewingConditions):
        cam = Cam16.from_int(self.to_int())
        viewed_in_vc = cam.xyz_in_viewing_conditions(vc)
        recast_in_vc = Cam16.from_xyz_in_viewing_conditions(
            viewed_in_vc[0], viewed_in_vc[1], viewed_in_vc[2], ViewingConditions.make()
        )
        recast_hct = Hct.from_hct(
            recast_in_vc.hue, recast_in_vc.chroma, lstar_from_y(viewed_in_vc[1])
        )
        return recast_hct
