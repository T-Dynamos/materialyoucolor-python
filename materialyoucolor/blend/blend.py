from materialyoucolor.hct import Hct
from materialyoucolor.hct.cam16 import Cam16
from materialyoucolor.utils.math_utils import (
    sanitize_degrees_double,
    difference_degrees,
    rotation_direction,
)
from materialyoucolor.utils.color_utils import lstar_from_argb


class Blend:
    @staticmethod
    def harmonize(design_color: int, source_color: int) -> int:
        from_hct = Hct.from_int(design_color)
        to_hct = Hct.from_int(source_color)
        difference_degrees_ = difference_degrees(from_hct.hue, to_hct.hue)
        rotation_degrees = min(difference_degrees_ * 0.5, 15.0)
        output_hue = sanitize_degrees_double(
            from_hct.hue
            + rotation_degrees * rotation_direction(from_hct.hue, to_hct.hue)
        )
        return Hct.from_hct(output_hue, from_hct.chroma, from_hct.tone).to_int()

    @staticmethod
    def hct_hue(from_: int, to: int, amount: int) -> int:
        ucs = Blend.cam16_ucs(from_, to, amount)
        ucs_cam = Cam16.from_int(ucs)
        from_cam = Cam16.from_int(from_)
        blended = Hct.from_hct(ucs_cam.hue, from_cam.chroma, lstar_from_argb(from_))
        return blended.to_int()

    @staticmethod
    def cam16_ucs(from_: int, to: int, amount: float) -> int:
        from_cam = Cam16.from_int(from_)
        to_cam = Cam16.from_int(to)
        from_j = from_cam.jstar
        from_a = from_cam.astar
        from_b = from_cam.bstar
        to_j = to_cam.jstar
        to_a = to_cam.astar
        to_b = to_cam.bstar
        jstar = from_j + (to_j - from_j) * amount
        astar = from_a + (to_a - from_a) * amount
        bstar = from_b + (to_b - from_b) * amount
        return Cam16.from_ucs(jstar, astar, bstar).to_int()
