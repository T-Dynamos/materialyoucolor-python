import math

from materialyoucolor.utils.math_utils import (
    signum,
    matrix_multiply,
    sanitize_degrees_double,
)
from materialyoucolor.utils.color_utils import (
    argb_from_lstar,
    argb_from_linrgb,
    y_from_lstar,
)
from materialyoucolor.hct.cam16 import Cam16
from materialyoucolor.hct.viewing_conditions import ViewingConditions


class HctSolver:
    SCALED_DISCOUNT_FROM_LINRGB = [
        [
            0.001200833568784504,
            0.002389694492170889,
            0.0002795742885861124,
        ],
        [
            0.0005891086651375999,
            0.0029785502573438758,
            0.0003270666104008398,
        ],
        [
            0.00010146692491640572,
            0.0005364214359186694,
            0.0032979401770712076,
        ],
    ]

    LINRGB_FROM_SCALED_DISCOUNT = [
        [
            1373.2198709594231,
            -1100.4251190754821,
            -7.278681089101213,
        ],
        [
            -271.815969077903,
            559.6580465940733,
            -32.46047482791194,
        ],
        [
            1.9622899599665666,
            -57.173814538844006,
            308.7233197812385,
        ],
    ]

    Y_FROM_LINRGB = [0.2126, 0.7152, 0.0722]

    CRITICAL_PLANES = [
        0.015176349177441876,
        0.045529047532325624,
        0.07588174588720938,
        0.10623444424209313,
        0.13658714259697685,
        0.16693984095186062,
        0.19729253930674434,
        0.2276452376616281,
        0.2579979360165119,
        0.28835063437139563,
        0.3188300904430532,
        0.350925934958123,
        0.3848314933096426,
        0.42057480301049466,
        0.458183274052838,
        0.4976837250274023,
        0.5391024159806381,
        0.5824650784040898,
        0.6277969426914107,
        0.6751227633498623,
        0.7244668422128921,
        0.775853049866786,
        0.829304845476233,
        0.8848452951698498,
        0.942497089126609,
        1.0022825574869039,
        1.0642236851973577,
        1.1283421258858297,
        1.1946592148522128,
        1.2631959812511864,
        1.3339731595349034,
        1.407011200216447,
        1.4823302800086415,
        1.5599503113873272,
        1.6398909516233677,
        1.7221716113234105,
        1.8068114625156377,
        1.8938294463134073,
        1.9832442801866852,
        2.075074464868551,
        2.1693382909216234,
        2.2660538449872063,
        2.36523901573795,
        2.4669114995532007,
        2.5710888059345764,
        2.6777882626779785,
        2.7870270208169257,
        2.898822059350997,
        3.0131901897720907,
        3.1301480604002863,
        3.2497121605402226,
        3.3718988244681087,
        3.4967242352587946,
        3.624204428461639,
        3.754355295633311,
        3.887192587735158,
        4.022731918402185,
        4.160988767090289,
        4.301978482107941,
        4.445716283538092,
        4.592217266055746,
        4.741496401646282,
        4.893568542229298,
        5.048448422192488,
        5.20615066083972,
        5.3666897647573375,
        5.5300801301023865,
        5.696336044816294,
        5.865471690767354,
        6.037501145825082,
        6.212438385869475,
        6.390297286737924,
        6.571091626112461,
        6.7548350853498045,
        6.941541251256611,
        7.131223617812143,
        7.323895587840543,
        7.5195704746346665,
        7.7182615035334345,
        7.919981813454504,
        8.124744458384042,
        8.332562408825165,
        8.543448553206703,
        8.757415699253682,
        8.974476575321063,
        9.194643831691977,
        9.417930041841839,
        9.644347703669503,
        9.873909240696694,
        10.106627003236781,
        10.342513269534024,
        10.58158024687427,
        10.8238400726681,
        11.069304815507364,
        11.317986476196008,
        11.569896988756009,
        11.825048221409341,
        12.083451977536606,
        12.345119996613247,
        12.610063955123938,
        12.878295467455942,
        13.149826086772048,
        13.42466730586372,
        13.702830557985108,
        13.984327217668513,
        14.269168601521828,
        14.55736596900856,
        14.848930523210871,
        15.143873411576273,
        15.44220572664832,
        15.743938506781891,
        16.04908273684337,
        16.35764934889634,
        16.66964922287304,
        16.985093187232053,
        17.30399201960269,
        17.62635644741625,
        17.95219714852476,
        18.281524751807332,
        18.614349837764564,
        18.95068293910138,
        19.290534541298456,
        19.633915083172692,
        19.98083495742689,
        20.331304511189067,
        20.685334046541502,
        21.042933821039977,
        21.404114048223256,
        21.76888489811322,
        22.137256497705877,
        22.50923893145328,
        22.884842241736916,
        23.264076429332462,
        23.6469514538663,
        24.033477234264016,
        24.42366364919083,
        24.817520537484558,
        25.21505769858089,
        25.61628489293138,
        26.021211842414342,
        26.429848230738664,
        26.842203703840827,
        27.258287870275353,
        27.678110301598522,
        28.10168053274597,
        28.529008062403893,
        28.96010235337422,
        29.39497283293396,
        29.83362889318845,
        30.276079891419332,
        30.722335150426627,
        31.172403958865512,
        31.62629557157785,
        32.08401920991837,
        32.54558406207592,
        33.010999283389665,
        33.4802739966603,
        33.953417292456834,
        34.430438229418264,
        34.911345834551085,
        35.39614910352207,
        35.88485700094671,
        36.37747846067349,
        36.87402238606382,
        37.37449765026789,
        37.87891309649659,
        38.38727753828926,
        38.89959975977785,
        39.41588851594697,
        39.93615253289054,
        40.460400508064545,
        40.98864111053629,
        41.520882981230194,
        42.05713473317016,
        42.597404951718396,
        43.141702194811224,
        43.6900349931913,
        44.24241185063697,
        44.798841244188324,
        45.35933162437017,
        45.92389141541209,
        46.49252901546552,
        47.065252796817916,
        47.64207110610409,
        48.22299226451468,
        48.808024568002054,
        49.3971762874833,
        49.9904556690408,
        50.587870934119984,
        51.189430279724725,
        51.79514187861014,
        52.40501387947288,
        53.0190544071392,
        53.637271562750364,
        54.259673423945976,
        54.88626804504493,
        55.517063457223934,
        56.15206766869424,
        56.79128866487574,
        57.43473440856916,
        58.08241284012621,
        58.734331877617365,
        59.39049941699807,
        60.05092333227251,
        60.715611475655585,
        61.38457167773311,
        62.057811747619894,
        62.7353394731159,
        63.417162620860914,
        64.10328893648692,
        64.79372614476921,
        65.48848194977529,
        66.18756403501224,
        66.89098006357258,
        67.59873767827808,
        68.31084450182222,
        69.02730813691093,
        69.74813616640164,
        70.47333615344107,
        71.20291564160104,
        71.93688215501312,
        72.67524319850172,
        73.41800625771542,
        74.16517879925733,
        74.9167682708136,
        75.67278210128072,
        76.43322770089146,
        77.1981124613393,
        77.96744375590167,
        78.74122893956174,
        79.51947534912904,
        80.30219030335869,
        81.08938110306934,
        81.88105503125999,
        82.67721935322541,
        83.4778813166706,
        84.28304815182372,
        85.09272707154808,
        85.90692527145302,
        86.72564993000343,
        87.54890820862819,
        88.3767072518277,
        89.2090541872801,
        90.04595612594655,
        90.88742016217518,
        91.73345337380438,
        92.58406282226491,
        93.43925555268066,
        94.29903859396902,
        95.16341895893969,
        96.03240364439274,
        96.9059996312159,
        97.78421388448044,
        98.6670533535366,
        99.55452497210776,
    ]

    @staticmethod
    def sanitize_radians(angle: float) -> float:
        return (angle + math.pi * 8) % (math.pi * 2)

    @staticmethod
    def true_delinearized(rgb_component: float) -> float:
        normalized = rgb_component / 100.0
        delinearized = 0.0
        if normalized <= 0.0031308:
            delinearized = normalized * 12.92
        else:
            delinearized = 1.055 * pow(normalized, 1.0 / 2.4) - 0.055
        return delinearized * 255.0

    @staticmethod
    def chromatic_adaptation(component: float) -> float:
        af = pow(abs(component), 0.42)
        return signum(component) * 400.0 * af / (af + 27.13)

    @staticmethod
    def hue_of(linrgb: list[float]) -> float:
        scaled_discount = matrix_multiply(linrgb, HctSolver.SCALED_DISCOUNT_FROM_LINRGB)
        r_a = HctSolver.chromatic_adaptation(scaled_discount[0])
        g_a = HctSolver.chromatic_adaptation(scaled_discount[1])
        b_a = HctSolver.chromatic_adaptation(scaled_discount[2])
        a = (11.0 * r_a + -12.0 * g_a + b_a) / 11.0
        b = (r_a + g_a - 2.0 * b_a) / 9.0
        return math.atan2(b, a)

    @staticmethod
    def are_in_cyclic_order(a: float, b: float, c: float) -> bool:
        delta_ab = HctSolver.sanitize_radians(b - a)
        delta_ac = HctSolver.sanitize_radians(c - a)
        return delta_ab < delta_ac

    @staticmethod
    def intercept(source: float, mid: float, target: float) -> float:
        return (mid - source) / (target - source)

    @staticmethod
    def lerp_point(source: list[float], t: float, target: list[float]) -> list[float]:
        return [
            source[0] + (target[0] - source[0]) * t,
            source[1] + (target[1] - source[1]) * t,
            source[2] + (target[2] - source[2]) * t,
        ]

    @staticmethod
    def set_coordinate(
        source: list[float], coordinate: float, target: list[float], axis: int
    ) -> list[float]:
        t = HctSolver.intercept(source[axis], coordinate, target[axis])
        return HctSolver.lerp_point(source, t, target)

    @staticmethod
    def is_bounded(x: float) -> bool:
        return 0.0 <= x <= 100.0

    @staticmethod
    def nth_vertex(y: float, n: float) -> list[float]:
        kr = HctSolver.Y_FROM_LINRGB[0]
        kg = HctSolver.Y_FROM_LINRGB[1]
        kb = HctSolver.Y_FROM_LINRGB[2]
        coord_a = 0.0 if n % 4 <= 1 else 100.0
        coord_b = 0.0 if n % 2 == 0 else 100.0

        if n < 4:
            g = coord_a
            b = coord_b
            r = (y - g * kg - b * kb) / kr
            if HctSolver.is_bounded(r):
                return [r, g, b]
            else:
                return [-1.0, -1.0, -1.0]
        elif n < 8:
            b = coord_a
            r = coord_b
            g = (y - r * kr - b * kb) / kg
            if HctSolver.is_bounded(g):
                return [r, g, b]
            else:
                return [-1.0, -1.0, -1.0]
        else:
            r = coord_a
            g = coord_b
            b = (y - r * kr - g * kg) / kb
            if HctSolver.is_bounded(b):
                return [r, g, b]
            else:
                return [-1.0, -1.0, -1.0]

    @staticmethod
    def bisect_to_segment(y: float, target_hue: float) -> list[list[float]]:
        left = [-1.0, -1.0, -1.0]
        right = left
        left_hue = 0.0
        right_hue = 0.0
        initialized = False
        uncut = True

        for n in range(12):
            mid = HctSolver.nth_vertex(y, n)

            if mid[0] < 0:
                continue

            mid_hue = HctSolver.hue_of(mid)

            if not initialized:
                left = mid
                right = mid
                left_hue = mid_hue
                right_hue = mid_hue
                initialized = True
                continue

            if uncut or HctSolver.are_in_cyclic_order(left_hue, mid_hue, right_hue):
                uncut = False

                if HctSolver.are_in_cyclic_order(left_hue, target_hue, mid_hue):
                    right = mid
                    right_hue = mid_hue
                else:
                    left = mid
                    left_hue = mid_hue

        return [left, right]

    @staticmethod
    def midpoint(a: list[float], b: list[float]) -> list[float]:
        return [
            (a[0] + b[0]) / 2,
            (a[1] + b[1]) / 2,
            (a[2] + b[2]) / 2,
        ]

    @staticmethod
    def critical_plane_below(x: float) -> float:
        return math.floor(x - 0.5)

    @staticmethod
    def critical_plane_above(x: float) -> float:
        return math.ceil(x - 0.5)

    @staticmethod
    def bisect_to_limit(y: float, target_hue: float) -> list[float]:
        segment = HctSolver.bisect_to_segment(y, target_hue)
        left = segment[0]
        left_hue = HctSolver.hue_of(left)
        right = segment[1]

        for axis in range(3):
            if left[axis] != right[axis]:
                l_plane = -1
                r_plane = 255

                if left[axis] < right[axis]:
                    l_plane = HctSolver.critical_plane_below(
                        HctSolver.true_delinearized(left[axis])
                    )
                    r_plane = HctSolver.critical_plane_above(
                        HctSolver.true_delinearized(right[axis])
                    )
                else:
                    l_plane = HctSolver.critical_plane_above(
                        HctSolver.true_delinearized(left[axis])
                    )
                    r_plane = HctSolver.critical_plane_below(
                        HctSolver.true_delinearized(right[axis])
                    )

                for _ in range(8):
                    if abs(r_plane - l_plane) <= 1:
                        break
                    else:
                        m_plane = math.floor((l_plane + r_plane) / 2.0)
                        mid_plane_coordinate = HctSolver.CRITICAL_PLANES[m_plane]
                        mid = HctSolver.set_coordinate(
                            left, mid_plane_coordinate, right, axis
                        )
                        mid_hue = HctSolver.hue_of(mid)

                        if HctSolver.are_in_cyclic_order(left_hue, target_hue, mid_hue):
                            right = mid
                            r_plane = m_plane
                        else:
                            left = mid
                            left_hue = mid_hue
                            l_plane = m_plane

        return HctSolver.midpoint(left, right)

    @staticmethod
    def inverse_chromatic_adaptation(adapted: float) -> float:
        adapted_abs = abs(adapted)
        base = max(0, 27.13 * adapted_abs / (400.0 - adapted_abs))
        return signum(adapted) * math.pow(base, 1.0 / 0.42)

    @staticmethod
    def find_result_by_j(hue_radians: float, chroma: float, y: float) -> int:
        j = math.sqrt(y) * 11.0
        viewing_conditions = ViewingConditions.DEFAULT()
        t_inner_coeff = 1 / math.pow(1.64 - math.pow(0.29, viewing_conditions.n), 0.73)
        e_hue = 0.25 * (math.cos(hue_radians + 2.0) + 3.8)
        p1 = e_hue * (50000.0 / 13.0) * viewing_conditions.nc * viewing_conditions.ncb
        h_sin = math.sin(hue_radians)
        h_cos = math.cos(hue_radians)

        for iteration_round in range(5):
            j_normalized = j / 100.0
            alpha = (
                chroma / math.sqrt(j_normalized)
                if (chroma != 0.0 and j != 0.0)
                else 0.0
            )
            t = math.pow(alpha * t_inner_coeff, 1.0 / 0.9)
            ac = viewing_conditions.aw * math.pow(
                j_normalized, 1.0 / viewing_conditions.c / viewing_conditions.z
            )
            p2 = ac / viewing_conditions.nbb
            gamma = (
                23.0
                * (p2 + 0.305)
                * t
                / (23.0 * p1 + 11 * t * h_cos + 108.0 * t * h_sin)
            )
            a = gamma * h_cos
            b = gamma * h_sin
            r_a = (460.0 * p2 + 451.0 * a + 288.0 * b) / 1403.0
            g_a = (460.0 * p2 - 891.0 * a - 261.0 * b) / 1403.0
            b_a = (460.0 * p2 - 220.0 * a - 6300.0 * b) / 1403.0
            r_c_scaled = HctSolver.inverse_chromatic_adaptation(r_a)
            g_c_scaled = HctSolver.inverse_chromatic_adaptation(g_a)
            b_c_scaled = HctSolver.inverse_chromatic_adaptation(b_a)
            linrgb = matrix_multiply(
                [r_c_scaled, g_c_scaled, b_c_scaled],
                HctSolver.LINRGB_FROM_SCALED_DISCOUNT,
            )

            if linrgb[0] < 0 or linrgb[1] < 0 or linrgb[2] < 0:
                return 0

            kR = HctSolver.Y_FROM_LINRGB[0]
            kG = HctSolver.Y_FROM_LINRGB[1]
            kB = HctSolver.Y_FROM_LINRGB[2]
            fnj = kR * linrgb[0] + kG * linrgb[1] + kB * linrgb[2]

            if fnj <= 0:
                return 0

            if iteration_round == 4 or abs(fnj - y) < 0.002:
                if linrgb[0] > 100.01 or linrgb[1] > 100.01 or linrgb[2] > 100.01:
                    return 0
                return argb_from_linrgb(linrgb)

            j = j - (fnj - y) * j / (2 * fnj)

        return 0

    @staticmethod
    def solve_to_int(hue_degrees: float, chroma: float, lstar: float) -> int:
        if chroma < 0.0001 or lstar < 0.0001 or lstar > 99.9999:
            return argb_from_lstar(lstar)

        hue_degrees = sanitize_degrees_double(hue_degrees)
        hue_radians = hue_degrees / 180 * math.pi
        y = y_from_lstar(lstar)
        exact_answer = HctSolver.find_result_by_j(hue_radians, chroma, y)

        if exact_answer != 0:
            return exact_answer

        linrgb = HctSolver.bisect_to_limit(y, hue_radians)
        return argb_from_linrgb(linrgb)

    @staticmethod
    def solve_to_cam(hueDegrees: float, chroma: float, lstar: float) -> Cam16:
        return Cam16.from_int(int(HctSolver.solve_to_int(hueDegrees, chroma, lstar)))
