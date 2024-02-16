from materialyoucolor.utils.math_utils import matrix_multiply, clamp_int

SRGB_TO_XYZ = [
    [0.41233895, 0.35762064, 0.18051042],
    [0.2126, 0.7152, 0.0722],
    [0.01932141, 0.11916382, 0.95034478],
]

XYZ_TO_SRGB = [
    [
        3.2413774792388685,
        -1.5376652402851851,
        -0.49885366846268053,
    ],
    [
        -0.9691452513005321,
        1.8758853451067872,
        0.04156585616912061,
    ],
    [
        0.05562093689691305,
        -0.20395524564742123,
        1.0571799111220335,
    ],
]

WHITE_POINT_D65 = [95.047, 100.0, 108.883]


def argb_from_rgb(red: float, green: float, blue: float, alpha=255) -> int:
    return (
        alpha << 24 | (int(red) & 255) << 16 | (int(green) & 255) << 8 | int(blue) & 255
    )


def argb_from_linrgb(linrgb: list[float]) -> int:
    r = delinearized(linrgb[0])
    g = delinearized(linrgb[1])
    b = delinearized(linrgb[2])
    return argb_from_rgb(r, g, b)


def alpha_from_argb(argb) -> float:
    return (argb >> 24) & 255


def red_from_argb(argb) -> float:
    return (argb >> 16) & 255


def green_from_argb(argb) -> float:
    return (argb >> 8) & 255


def blue_from_argb(argb) -> float:
    return argb & 255


def is_opaque(argb) -> bool:
    return alpha_from_argb(argb) >= 255


def argb_from_xyz(x, y, z) -> int:
    matrix = XYZ_TO_SRGB
    linear_r = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z
    linear_g = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z
    linear_b = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z
    r = delinearized(linear_r)
    g = delinearized(linear_g)
    b = delinearized(linear_b)
    return argb_from_rgb(r, g, b)


def xyz_from_argb(argb) -> list[float]:
    r = linearized(red_from_argb(argb))
    g = linearized(green_from_argb(argb))
    b = linearized(blue_from_argb(argb))
    return matrix_multiply([r, g, b], SRGB_TO_XYZ)


def argb_from_lab(l, a, b) -> float:
    white_point = WHITE_POINT_D65
    fy = (l + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0
    x_normalized = lab_invf(fx)
    y_normalized = lab_invf(fy)
    z_normalized = lab_invf(fz)
    x = x_normalized * white_point[0]
    y = y_normalized * white_point[1]
    z = z_normalized * white_point[2]
    return argb_from_xyz(x, y, z)


def lab_from_argb(argb: int) -> list[float]:
    linear_r = linearized(red_from_argb(argb))
    linear_g = linearized(green_from_argb(argb))
    linear_b = linearized(blue_from_argb(argb))
    matrix = SRGB_TO_XYZ
    x = matrix[0][0] * linear_r + matrix[0][1] * linear_g + matrix[0][2] * linear_b
    y = matrix[1][0] * linear_r + matrix[1][1] * linear_g + matrix[1][2] * linear_b
    z = matrix[2][0] * linear_r + matrix[2][1] * linear_g + matrix[2][2] * linear_b
    white_point = WHITE_POINT_D65
    x_normalized = x / white_point[0]
    y_normalized = y / white_point[1]
    z_normalized = z / white_point[2]
    fx = lab_f(x_normalized)
    fy = lab_f(y_normalized)
    fz = lab_f(z_normalized)
    l = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return [l, a, b]


def argb_from_lstar(lstar: float) -> int:
    y = y_from_lstar(lstar)
    component = delinearized(y)
    return argb_from_rgb(component, component, component)


def lstar_from_argb(argb: int) -> float:
    y = xyz_from_argb(argb)[1]
    return 116.0 * lab_f(y / 100.0) - 16.0


def y_from_lstar(lstar: float) -> float:
    return 100.0 * lab_invf((lstar + 16.0) / 116.0)


def srgb_to_argb(srgb):
    return int("0xff{:06X}".format(0xFFFFFF & srgb), 16)


def lstar_from_y(y: float) -> float:
    return lab_f(y / 100.0) * 116.0 - 16.0


def linearized(rgb_component: float) -> float:
    normalized = rgb_component / 255.0
    if normalized <= 0.040449936:
        return normalized / 12.92 * 100.0
    else:
        return pow((normalized + 0.055) / 1.055, 2.4) * 100.0


def delinearized(rgb_component: float) -> float:
    normalized = rgb_component / 100.0
    if normalized <= 0.0031308:
        delinearized = normalized * 12.92
    else:
        delinearized = 1.055 * pow(normalized, 1.0 / 2.4) - 0.055
    return clamp_int(0, 255, round(delinearized * 255))


def white_point_d65() -> list[float]:
    return WHITE_POINT_D65


class Rgba:
    r: float
    g: float
    b: float
    a: float


def rgba_from_argb(argb: int) -> list[float]:
    r = red_from_argb(argb)
    g = green_from_argb(argb)
    b = blue_from_argb(argb)
    a = alpha_from_argb(argb)
    return [r, g, b, a]


def argb_from_rgba(rgba: list[int]) -> int:
    r_value = clamp_component(rgba[0])
    g_value = clamp_component(rgba[1])
    b_value = clamp_component(rgba[2])
    a_value = clamp_component(rgba[3])
    return (a_value << 24) | (r_value << 16) | (g_value << 8) | b_value


def argb_from_rgba_01(rgba: list[int]) -> int:
    return argb_from_rgba([int(_ * 255) for _ in rgba])


def clamp_component(value: int) -> int:
    if value < 0:
        return 0
    if value > 255:
        return 255
    return value


def lab_f(t: float) -> float:
    e = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    if t > e:
        return pow(t, 1.0 / 3.0)
    else:
        return (kappa * t + 16) / 116


def lab_invf(ft: float) -> float:
    e = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    ft3 = ft * ft * ft
    if ft3 > e:
        return ft3
    else:
        return (116 * ft - 16) / kappa
