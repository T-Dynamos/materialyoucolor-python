from materialyoucolor.utils.math_utils import lerp


class ContrastCurve:
    def __init__(self, low: float, normal: float, medium: float, high: float):
        self.low = low
        self.normal = normal
        self.medium = medium
        self.high = high

    def get(self, contrast_level: float) -> float:
        if contrast_level <= -1.0:
            return self.low
        elif contrast_level < 0.0:
            return lerp(self.low, self.normal, (contrast_level - (-1)) / 1)
        elif contrast_level < 0.5:
            return lerp(self.normal, self.medium, (contrast_level - 0) / 0.5)
        elif contrast_level < 1.0:
            return lerp(self.medium, self.high, (contrast_level - 0.5) / 0.5)
        else:
            return self.high
