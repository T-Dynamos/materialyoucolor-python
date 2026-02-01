from materialyoucolor.hct.cam16 import Cam16
from materialyoucolor.hct.hct import Hct
from materialyoucolor.utils.color_utils import lstar_from_argb
from materialyoucolor.utils.math_utils import (
    difference_degrees,
    rotation_direction,
    sanitize_degrees_double,
)


class Blend:
    """
    Functions for blending in HCT and CAM16.
    """

    @staticmethod
    def harmonize(design_color: int, source_color: int) -> int:
        """
        Blend the design color's HCT hue towards the key color's HCT
        hue, in a way that leaves the original color recognizable and
        recognizably shifted towards the key color.
        """
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
    def hct_hue(from_argb: int, to_argb: int, amount: float) -> int:
        """
        Blends hue from one color into another. The chroma and tone of
        the original color are maintained.
        """
        ucs = Blend.cam16_ucs(from_argb, to_argb, amount)
        ucs_cam = Cam16.from_int(ucs)
        from_cam = Cam16.from_int(from_argb)
        blended = Hct.from_hct(ucs_cam.hue, from_cam.chroma, lstar_from_argb(from_argb))
        return blended.to_int()

    @staticmethod
    def cam16_ucs(from_argb: int, to_argb: int, amount: float) -> int:
        """
        Blend in CAM16-UCS space.
        """
        from_cam = Cam16.from_int(from_argb)
        to_cam = Cam16.from_int(to_argb)
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
