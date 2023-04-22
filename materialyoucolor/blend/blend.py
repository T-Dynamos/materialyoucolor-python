from materialyoucolor.hct.cam16 import Cam16
from materialyoucolor.hct.hct import Hct
from materialyoucolor.utils.math_utils import sanitizeDegreesDouble, differenceDegrees


class Blend:
    @staticmethod
    def harmonize(designColor, sourceColor):
        fromHct = Hct.fromInt(designColor)
        toHct = Hct.fromInt(sourceColor)
        differenceDegrees_v = differenceDegrees(fromHct.hue, toHct.hue)
        rotationDegrees = min(differenceDegrees_v * 0.5, 15.0)
        outputHue = sanitizeDegreesDouble(
            fromHct.hue
            + rotationDegrees * Blend.rotationDirection(fromHct.hue, toHct.hue)
        )
        return Hct.fromHct(outputHue, fromHct.chroma, fromHct.tone).toInt()

    @staticmethod
    def hctHue(from_v, to, amount):
        ucs = Blend.cam16Ucs(from_v, to, amount)
        ucsCam = Cam16.fromInt(ucs)
        fromCam = Cam16.fromInt(from_v)
        blended = Hct.fromHct(ucsCam.hue, fromCam.chroma, lstarFromArgb(from_v))
        return blended.toInt()

    @staticmethod
    def cam16Ucs(from_v, to, amount):
        fromCam = Cam16.fromInt(from_v)
        toCam = Cam16.fromInt(to)
        fromJ = fromCam.jstar
        fromA = fromCam.astar
        fromB = fromCam.bstar
        toJ = toCam.jstar
        toA = toCam.astar
        toB = toCam.bstar
        jstar = fromJ + (toJ - fromJ) * amount
        astar = fromA + (toA - fromA) * amount
        bstar = fromB + (toB - fromB) * amount
        return Cam16.fromUcs(jstar, astar, bstar).toInt()

    @staticmethod
    def rotationDirection(from_v, to):
        a = to - from_v
        b = to - from_v + 360.0
        c = to - from_v - 360.0
        aAbs = abs(a)
        bAbs = abs(b)
        cAbs = abs(c)
        if aAbs <= bAbs and aAbs <= cAbs:
            return 1.0 if a >= 0.0 else -1.0
        elif bAbs <= aAbs and bAbs <= cAbs:
            return 1.0 if b >= 0.0 else -1.0
        else:
            return 1.0 if c >= 0.0 else -1.0
