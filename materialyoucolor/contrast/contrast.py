from materialyoucolor.utils.math_utils import clamp_double
from materialyoucolor.utils.color_utils import y_from_lstar, lstar_from_y


class Contrast:
    @staticmethod
    def ratio_of_tones(tone_a: float, tone_b: float) -> float:
        tone_a = clamp_double(0.0, 100.0, tone_a)
        tone_b = clamp_double(0.0, 100.0, tone_b)
        return Contrast.ratio_of_ys(y_from_lstar(tone_a), y_from_lstar(tone_b))

    @staticmethod
    def ratio_of_ys(y1: float, y2: float) -> float:
        lighter = y1 if y1 > y2 else y2
        darker = y1 if lighter == y2 else y2
        return (lighter + 5.0) / (darker + 5.0)

    @staticmethod
    def lighter(tone: float, ratio: float) -> float:
        if tone < 0.0 or tone > 100.0:
            return -1.0

        dark_y = y_from_lstar(tone)
        light_y = ratio * (dark_y + 5.0) - 5.0
        real_contrast = Contrast.ratio_of_ys(light_y, dark_y)
        delta = abs(real_contrast - ratio)
        if real_contrast < ratio and delta > 0.04:
            return -1

        return_value = lstar_from_y(light_y) + 0.4
        if return_value < 0 or return_value > 100:
            return -1.0
        return return_value

    @staticmethod
    def darker(tone: float, ratio: float) -> float:
        if tone < 0.0 or tone > 100.0:
            return -1.0

        light_y = y_from_lstar(tone)
        dark_y = (light_y + 5.0) / ratio - 5.0
        real_contrast = Contrast.ratio_of_ys(light_y, dark_y)

        delta = abs(real_contrast - ratio)
        if real_contrast < ratio and delta > 0.04:
            return -1

        return_value = lstar_from_y(dark_y) - 0.4
        if return_value < 0 or return_value > 100:
            return -1
        return return_value

    @staticmethod
    def lighter_unsafe(tone, ratio):
        lighter_safe = Contrast.lighter(tone, ratio)
        return 100.0 if lighter_safe < 0.0 else lighter_safe

    @staticmethod
    def darker_unsafe(tone, ratio):
        darker_safe = Contrast.darker(tone, ratio)
        return 0.0 if darker_safe < 0.0 else darker_safe
