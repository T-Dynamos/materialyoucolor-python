from materialyoucolor.utils.color_utils import whitePointD65, yFromLstar
from materialyoucolor.utils.math_utils import clampInt, lerp
import math


class ViewingConditions:
    def __init__(self, n, aw, nbb, ncb, c, nc, rgbD, fl, fLRoot, z):
        self.n = n
        self.aw = aw
        self.nbb = nbb
        self.ncb = ncb
        self.c = c
        self.nc = nc
        self.rgbD = rgbD
        self.fl = fl
        self.fLRoot = fLRoot
        self.z = z

    @staticmethod
    def make(
        whitePoint=whitePointD65(),
        adaptingLuminance=(200.0 / math.pi) * yFromLstar(50.0) / 100.0,
        backgroundLstar=50.0,
        surround=2.0,
        discountingIlluminant=False,
    ):
        xyz = whitePoint
        rW = xyz[0] * 0.401288 + xyz[1] * 0.650173 + xyz[2] * -0.051461
        gW = xyz[0] * -0.250268 + xyz[1] * 1.204414 + xyz[2] * 0.045854
        bW = xyz[0] * -0.002079 + xyz[1] * 0.048952 + xyz[2] * 0.953127
        f = 0.8 + surround / 10.0
        c = (
            lerp(0.59, 0.69, (f - 0.9) * 10.0)
            if f >= 0.9
            else lerp(0.525, 0.59, (f - 0.8) * 10.0)
        )
        d = (
            1.0
            if discountingIlluminant
            else f * (1.0 - (1.0 / 3.6) * math.exp((-adaptingLuminance - 42.0) / 92.0))
        )
        d = 1.0 if d > 1.0 else 0.0 if d < 0.0 else d
        nc = f
        rgbD = [
            d * (100.0 / rW) + 1.0 - d,
            d * (100.0 / gW) + 1.0 - d,
            d * (100.0 / bW) + 1.0 - d,
        ]
        k = 1.0 / (5.0 * adaptingLuminance + 1.0)
        k4 = k * k * k * k
        k4F = 1.0 - k4
        fl = k4 * adaptingLuminance + 0.1 * k4F * k4F * (
            (5.0 * adaptingLuminance) ** (1.0 / 3)
        )
        n = yFromLstar(backgroundLstar) / whitePoint[1]
        z = 1.48 + math.sqrt(n)
        nbb = 0.725 / pow(n, 0.2)
        ncb = nbb
        rgbAFactors = [
            pow((fl * rgbD[0] * rW) / 100.0, 0.42),
            pow((fl * rgbD[1] * gW) / 100.0, 0.42),
            pow((fl * rgbD[2] * bW) / 100.0, 0.42),
        ]
        rgbA = [
            (400.0 * rgbAFactors[0]) / (rgbAFactors[0] + 27.13),
            (400.0 * rgbAFactors[1]) / (rgbAFactors[1] + 27.13),
            (400.0 * rgbAFactors[2]) / (rgbAFactors[2] + 27.13),
        ]
        aw = (2.0 * rgbA[0] + rgbA[1] + 0.05 * rgbA[2]) * nbb
        return ViewingConditions(n, aw, nbb, ncb, c, nc, rgbD, fl, pow(fl, 0.25), z)


ViewingConditions.DEFAULT = ViewingConditions.make()
