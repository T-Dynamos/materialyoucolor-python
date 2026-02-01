import math

from materialyoucolor.hct.viewing_conditions import ViewingConditions
from materialyoucolor.utils.color_utils import argb_from_xyz, linearized
from materialyoucolor.utils.math_utils import sanitize_degrees_double, signum


class Cam16:
    def __init__(
        self,
        hue: float,
        chroma: float,
        j: float,
        q: float,
        m: float,
        s: float,
        jstar: float,
        astar: float,
        bstar: float,
    ):
        self.hue = hue
        self.chroma = chroma
        self.j = j
        self.q = q
        self.m = m
        self.s = s
        self.jstar = jstar
        self.astar = astar
        self.bstar = bstar

    def distance(self, other: "Cam16") -> float:
        d_j = self.jstar - other.jstar
        d_a = self.astar - other.astar
        d_b = self.bstar - other.bstar
        d_e_prime = math.sqrt(d_j * d_j + d_a * d_a + d_b * d_b)
        d_e = 1.41 * math.pow(d_e_prime, 0.63)
        return d_e

    @staticmethod
    def from_int(argb: int) -> "Cam16":
        return Cam16.from_int_in_viewing_conditions(argb, ViewingConditions.DEFAULT)

    @staticmethod
    def from_int_in_viewing_conditions(
        argb: int, viewing_conditions: ViewingConditions
    ) -> "Cam16":
        red = (argb & 0x00FF0000) >> 16
        green = (argb & 0x0000FF00) >> 8
        blue = argb & 0x000000FF
        red_l = linearized(red)
        green_l = linearized(green)
        blue_l = linearized(blue)
        x = 0.41233895 * red_l + 0.35762064 * green_l + 0.18051042 * blue_l
        y = 0.2126 * red_l + 0.7152 * green_l + 0.0722 * blue_l
        z = 0.01932141 * red_l + 0.11916382 * green_l + 0.95034478 * blue_l
        return Cam16.from_xyz_in_viewing_conditions(x, y, z, viewing_conditions)

    @staticmethod
    def from_xyz_in_viewing_conditions(
        x: float, y: float, z: float, viewing_conditions: ViewingConditions
    ) -> "Cam16":
        r_c = 0.401288 * x + 0.650173 * y - 0.051461 * z
        g_c = -0.250268 * x + 1.204414 * y + 0.045854 * z
        b_c = -0.002079 * x + 0.048952 * y + 0.953127 * z

        r_d = viewing_conditions.rgb_d[0] * r_c
        g_d = viewing_conditions.rgb_d[1] * g_c
        b_d = viewing_conditions.rgb_d[2] * b_c

        r_af = math.pow((viewing_conditions.fl * abs(r_d)) / 100.0, 0.42)
        g_af = math.pow((viewing_conditions.fl * abs(g_d)) / 100.0, 0.42)
        b_af = math.pow((viewing_conditions.fl * abs(b_d)) / 100.0, 0.42)

        r_a = (signum(r_d) * 400.0 * r_af) / (r_af + 27.13)
        g_a = (signum(g_d) * 400.0 * g_af) / (g_af + 27.13)
        b_a = (signum(b_d) * 400.0 * b_af) / (b_af + 27.13)

        a = (11.0 * r_a + -12.0 * g_a + b_a) / 11.0
        b = (r_a + g_a - 2.0 * b_a) / 9.0
        u = (20.0 * r_a + 20.0 * g_a + 21.0 * b_a) / 20.0
        p2 = (40.0 * r_a + 20.0 * g_a + b_a) / 20.0
        atan2 = math.atan2(b, a)
        atan_degrees = (atan2 * 180.0) / math.pi
        hue = sanitize_degrees_double(atan_degrees)
        hue_radians = (hue * math.pi) / 180.0

        ac = p2 * viewing_conditions.nbb
        j = 100.0 * math.pow(
            ac / viewing_conditions.aw, viewing_conditions.c * viewing_conditions.z
        )
        q = (
            (4.0 / viewing_conditions.c)
            * math.sqrt(j / 100.0)
            * (viewing_conditions.aw + 4.0)
            * viewing_conditions.f_l_root
        )
        hue_prime = hue + 360 if hue < 20.14 else hue
        e_hue = 0.25 * (math.cos((hue_prime * math.pi) / 180.0 + 2.0) + 3.8)
        p1 = (50000.0 / 13.0) * e_hue * viewing_conditions.nc * viewing_conditions.ncb
        t = (p1 * math.sqrt(a * a + b * b)) / (u + 0.305)
        alpha = math.pow(t, 0.9) * math.pow(
            1.64 - math.pow(0.29, viewing_conditions.n), 0.73
        )
        c = alpha * math.sqrt(j / 100.0)
        m = c * viewing_conditions.f_l_root
        s = 50.0 * math.sqrt(
            (alpha * viewing_conditions.c) / (viewing_conditions.aw + 4.0)
        )
        jstar = ((1.0 + 100.0 * 0.007) * j) / (1.0 + 0.007 * j)
        mstar = (1.0 / 0.0228) * math.log(1.0 + 0.0228 * m)
        astar = mstar * math.cos(hue_radians)
        bstar = mstar * math.sin(hue_radians)

        return Cam16(hue, c, j, q, m, s, jstar, astar, bstar)

    @staticmethod
    def from_jch(j: float, c: float, h: float) -> "Cam16":
        return Cam16.from_jch_in_viewing_conditions(j, c, h, ViewingConditions.DEFAULT)

    @staticmethod
    def from_jch_in_viewing_conditions(
        j: float, c: float, h: float, viewing_conditions: ViewingConditions
    ) -> "Cam16":
        q = (
            (4.0 / viewing_conditions.c)
            * math.sqrt(j / 100.0)
            * (viewing_conditions.aw + 4.0)
            * viewing_conditions.f_l_root
        )
        m = c * viewing_conditions.f_l_root
        alpha = c / math.sqrt(j / 100.0)
        s = 50.0 * math.sqrt(
            (alpha * viewing_conditions.c) / (viewing_conditions.aw + 4.0)
        )
        hue_radians = (h * math.pi) / 180.0
        jstar = ((1.0 + 100.0 * 0.007) * j) / (1.0 + 0.007 * j)
        mstar = (1.0 / 0.0228) * math.log(1.0 + 0.0228 * m)
        astar = mstar * math.cos(hue_radians)
        bstar = mstar * math.sin(hue_radians)
        return Cam16(h, c, j, q, m, s, jstar, astar, bstar)

    @staticmethod
    def from_ucs(jstar: float, astar: float, bstar: float) -> "Cam16":
        return Cam16.from_ucs_in_viewing_conditions(
            jstar, astar, bstar, ViewingConditions.DEFAULT
        )

    @staticmethod
    def from_ucs_in_viewing_conditions(
        jstar: float, astar: float, bstar: float, viewing_conditions: ViewingConditions
    ) -> "Cam16":
        a = astar
        b = bstar
        m = math.sqrt(a * a + b * b)
        M = (math.exp(m * 0.0228) - 1.0) / 0.0228
        c = M / viewing_conditions.f_l_root
        h = math.atan2(b, a) * (180.0 / math.pi)
        if h < 0.0:
            h += 360.0
        j = jstar / (1 - (jstar - 100) * 0.007)
        return Cam16.from_jch_in_viewing_conditions(j, c, h, viewing_conditions)

    def to_int(self) -> int:
        return self.viewed(ViewingConditions.DEFAULT)

    def viewed(self, viewing_conditions: ViewingConditions) -> int:
        xyz = self.xyz_in_viewing_conditions(viewing_conditions)
        return argb_from_xyz(xyz[0], xyz[1], xyz[2])

    def xyz_in_viewing_conditions(
        self, viewing_conditions: ViewingConditions
    ) -> list[float]:
        alpha = (
            0.0
            if (self.chroma == 0.0 or self.j == 0.0)
            else self.chroma / math.sqrt(self.j / 100.0)
        )

        t = math.pow(
            alpha / math.pow(1.64 - math.pow(0.29, viewing_conditions.n), 0.73),
            1.0 / 0.9,
        )
        h_rad = self.hue * math.pi / 180.0

        e_hue = 0.25 * (math.cos(h_rad + 2.0) + 3.8)
        ac = viewing_conditions.aw * math.pow(
            self.j / 100.0, 1.0 / viewing_conditions.c / viewing_conditions.z
        )
        p1 = e_hue * (50000.0 / 13.0) * viewing_conditions.nc * viewing_conditions.ncb

        p2 = ac / viewing_conditions.nbb

        h_sin = math.sin(h_rad)
        h_cos = math.cos(h_rad)

        gamma = (
            23.0 * (p2 + 0.305) * t / (23.0 * p1 + 11 * t * h_cos + 108.0 * t * h_sin)
        )
        a = gamma * h_cos
        b = gamma * h_sin
        r_a = (460.0 * p2 + 451.0 * a + 288.0 * b) / 1403.0
        g_a = (460.0 * p2 - 891.0 * a - 261.0 * b) / 1403.0
        b_a = (460.0 * p2 - 220.0 * a - 6300.0 * b) / 1403.0

        r_c_base = max(0, (27.13 * abs(r_a)) / (400.0 - abs(r_a)))
        r_c = (
            signum(r_a)
            * (100.0 / viewing_conditions.fl)
            * math.pow(r_c_base, 1.0 / 0.42)
        )
        g_c_base = max(0, (27.13 * abs(g_a)) / (400.0 - abs(g_a)))
        g_c = (
            signum(g_a)
            * (100.0 / viewing_conditions.fl)
            * math.pow(g_c_base, 1.0 / 0.42)
        )
        b_c_base = max(0, (27.13 * abs(b_a)) / (400.0 - abs(b_a)))
        b_c = (
            signum(b_a)
            * (100.0 / viewing_conditions.fl)
            * math.pow(b_c_base, 1.0 / 0.42)
        )
        r_f = r_c / viewing_conditions.rgb_d[0]
        g_f = g_c / viewing_conditions.rgb_d[1]
        b_f = b_c / viewing_conditions.rgb_d[2]

        x = 1.86206786 * r_f - 1.01125463 * g_f + 0.14918677 * b_f
        y = 0.38752654 * r_f + 0.62144744 * g_f - 0.00897398 * b_f
        z = -0.01584150 * r_f - 0.03412294 * g_f + 1.04996444 * b_f

        return [x, y, z]
