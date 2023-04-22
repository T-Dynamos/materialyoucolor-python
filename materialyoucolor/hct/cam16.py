from materialyoucolor.utils.color_utils import (
    redFromArgb,
    greenFromArgb,
    blueFromArgb,
    lstarFromArgb,
    linearized,
    argbFromXyz,
)
from materialyoucolor.utils.math_utils import signum, sanitizeDegreesDouble, clampDouble
from materialyoucolor.hct.viewing_conditions import ViewingConditions
import math


class Cam16:
    def __init__(self, hue, chroma, j, q, m, s, jstar, astar, bstar):
        self.hue = hue
        self.chroma = chroma
        self.j = j
        self.q = q
        self.m = m
        self.s = s
        self.jstar = jstar
        self.astar = astar
        self.bstar = bstar

    def distance(self, other):
        dJ = self.jstar - other.jstar
        dA = self.astar - other.astar
        dB = self.bstar - other.bstar
        dEPrime = math.sqrt(dJ * dJ + dA * dA + dB * dB)
        dE = 1.41 * pow(dEPrime, 0.63)
        return dE

    @staticmethod
    def fromInt(argb):
        return Cam16.fromIntInViewingConditions(argb, ViewingConditions.DEFAULT)

    @staticmethod
    def fromIntInViewingConditions(argb, viewingConditions):
        red = (argb & 0x00FF0000) >> 16
        green = (argb & 0x0000FF00) >> 8
        blue = argb & 0x000000FF
        redL = linearized(red)
        greenL = linearized(green)
        blueL = linearized(blue)
        x = 0.41233895 * redL + 0.35762064 * greenL + 0.18051042 * blueL
        y = 0.2126 * redL + 0.7152 * greenL + 0.0722 * blueL
        z = 0.01932141 * redL + 0.11916382 * greenL + 0.95034478 * blueL
        rC = 0.401288 * x + 0.650173 * y - 0.051461 * z
        gC = -0.250268 * x + 1.204414 * y + 0.045854 * z
        bC = -0.002079 * x + 0.048952 * y + 0.953127 * z
        rD = viewingConditions.rgbD[0] * rC
        gD = viewingConditions.rgbD[1] * gC
        bD = viewingConditions.rgbD[2] * bC
        rAF = pow((viewingConditions.fl * abs(rD)) / 100.0, 0.42)
        gAF = pow((viewingConditions.fl * abs(gD)) / 100.0, 0.42)
        bAF = pow((viewingConditions.fl * abs(bD)) / 100.0, 0.42)
        rA = (signum(rD) * 400.0 * rAF) / (rAF + 27.13)
        gA = (signum(gD) * 400.0 * gAF) / (gAF + 27.13)
        bA = (signum(bD) * 400.0 * bAF) / (bAF + 27.13)
        a = (11.0 * rA + -12.0 * gA + bA) / 11.0
        b = (rA + gA - 2.0 * bA) / 9.0
        u = (20.0 * rA + 20.0 * gA + 21.0 * bA) / 20.0
        p2 = (40.0 * rA + 20.0 * gA + bA) / 20.0
        atan2 = math.atan2(b, a)
        atanDegrees = (atan2 * 180.0) / math.pi
        hue = (
            atanDegrees + 360.0
            if atanDegrees < 0
            else atanDegrees - 360.0
            if atanDegrees >= 360
            else atanDegrees
        )
        hueRadians = (hue * math.pi) / 180.0
        ac = p2 * viewingConditions.nbb
        j = 100.0 * pow(
            ac / viewingConditions.aw, viewingConditions.c * viewingConditions.z
        )
        q = (
            (4.0 / viewingConditions.c)
            * math.sqrt(j / 100.0)
            * (viewingConditions.aw + 4.0)
            * viewingConditions.fLRoot
        )
        huePrime = hue + 360 if hue < 20.14 else hue
        eHue = 0.25 * (math.cos((huePrime * math.pi) / 180.0 + 2.0) + 3.8)
        p1 = (50000.0 / 13.0) * eHue * viewingConditions.nc * viewingConditions.ncb
        t = (p1 * math.sqrt(a * a + b * b)) / (u + 0.305)
        alpha = pow(t, 0.9) * pow(1.64 - pow(0.29, viewingConditions.n), 0.73)
        c = alpha * math.sqrt(j / 100.0)
        m = c * viewingConditions.fLRoot
        s = 50.0 * math.sqrt(
            (alpha * viewingConditions.c) / (viewingConditions.aw + 4.0)
        )
        jstar = ((1.0 + 100.0 * 0.007) * j) / (1.0 + 0.007 * j)
        mstar = (1.0 / 0.0228) * math.log(1.0 + 0.0228 * m)
        astar = mstar * math.cos(hueRadians)
        bstar = mstar * math.sin(hueRadians)
        return Cam16(hue, c, j, q, m, s, jstar, astar, bstar)

    @staticmethod
    def fromJch(j, c, h):
        return Cam16.fromJchInViewingConditions(j, c, h, ViewingConditions.DEFAULT)

    @staticmethod
    def fromJchInViewingConditions(j, c, h, viewingConditions):
        q = (
            (4.0 / viewingConditions.c)
            * math.sqrt(j / 100.0)
            * (viewingConditions.aw + 4.0)
            * viewingConditions.fLRoot
        )
        m = c * viewingConditions.fLRoot
        alpha = c / math.sqrt(j / 100.0)
        s = 50.0 * math.sqrt(
            (alpha * viewingConditions.c) / (viewingConditions.aw + 4.0)
        )
        hueRadians = (h * math.pi) / 180.0
        jstar = ((1.0 + 100.0 * 0.007) * j) / (1.0 + 0.007 * j)
        mstar = (1.0 / 0.0228) * math.log(1.0 + 0.0228 * m)
        astar = mstar * math.cos(hueRadians)
        bstar = mstar * math.sin(hueRadians)
        return Cam16(h, c, j, q, m, s, jstar, astar, bstar)

    @staticmethod
    def fromUcs(jstar, astar, bstar):
        return Cam16.fromUcsInViewingConditions(
            jstar, astar, bstar, ViewingConditions.DEFAULT
        )

    @staticmethod
    def fromUcsInViewingConditions(jstar, astar, bstar, viewingConditions):
        a = astar
        b = bstar
        m = math.sqrt(a * a + b * b)
        M = (math.exp(m * 0.0228) - 1.0) / 0.0228
        c = M / viewingConditions.fLRoot
        h = math.atan2(b, a) * (180.0 / math.pi)
        if h < 0.0:
            h += 360.0
        j = jstar / (1 - (jstar - 100) * 0.007)
        return Cam16.fromJchInViewingConditions(j, c, h, viewingConditions)

    def toInt(self):
        return self.viewed(ViewingConditions.DEFAULT)

    def viewed(self, viewingConditions):
        alpha = (
            0.0
            if self.chroma == 0.0 or self.j == 0.0
            else self.chroma / math.sqrt(self.j / 100.0)
        )
        t = pow(alpha / pow(1.64 - pow(0.29, viewingConditions.n), 0.73), 1.0 / 0.9)
        hRad = (self.hue * math.pi) / 180.0
        eHue = 0.25 * (math.cos(hRad + 2.0) + 3.8)
        ac = viewingConditions.aw * pow(
            self.j / 100.0, 1.0 / viewingConditions.c / viewingConditions.z
        )
        p1 = eHue * (50000.0 / 13.0) * viewingConditions.nc * viewingConditions.ncb
        p2 = ac / viewingConditions.nbb
        hSin = math.sin(hRad)
        hCos = math.cos(hRad)
        gamma = (23.0 * (p2 + 0.305) * t) / (
            23.0 * p1 + 11.0 * t * hCos + 108.0 * t * hSin
        )
        a = gamma * hCos
        b = gamma * hSin
        rA = (460.0 * p2 + 451.0 * a + 288.0 * b) / 1403.0
        gA = (460.0 * p2 - 891.0 * a - 261.0 * b) / 1403.0
        bA = (460.0 * p2 - 220.0 * a - 6300.0 * b) / 1403.0
        rCBase = max(0, (27.13 * abs(rA)) / (400.0 - abs(rA)))
        rC = signum(rA) * (100.0 / viewingConditions.fl) * pow(rCBase, 1.0 / 0.42)
        gCBase = max(0, (27.13 * abs(gA)) / (400.0 - abs(gA)))
        gC = signum(gA) * (100.0 / viewingConditions.fl) * pow(gCBase, 1.0 / 0.42)
        bCBase = max(0, (27.13 * abs(bA)) / (400.0 - abs(bA)))
        bC = signum(bA) * (100.0 / viewingConditions.fl) * pow(bCBase, 1.0 / 0.42)
        rF = rC / viewingConditions.rgbD[0]
        gF = gC / viewingConditions.rgbD[1]
        bF = bC / viewingConditions.rgbD[2]
        x = 1.86206786 * rF - 1.01125463 * gF + 0.14918677 * bF
        y = 0.38752654 * rF + 0.62144744 * gF - 0.00897398 * bF
        z = -0.01584150 * rF - 0.03412294 * gF + 1.04996444 * bF
        argb = argbFromXyz(x, y, z)
        return argb
