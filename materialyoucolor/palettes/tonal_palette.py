from materialyoucolor.hct import Hct
from materialyoucolor.utils.color_utils import rgba_from_argb
from materialyoucolor.utils.color_utils import argb_from_rgb


class KeyColor:
    def __init__(self, hue: float, requested_chroma: float):
        self.chroma_cache = {}
        self.max_chroma_value = 200.0
        self.hue = hue
        self.requested_chroma = requested_chroma

    def create(self):
        pivot_tone = 50
        tone_step_size = 1
        epsilon = 0.01
        lower_tone = 0
        upper_tone = 100
        while lower_tone < upper_tone:
            mid_tone = (lower_tone + upper_tone) // 2
            is_ascending = self.max_chroma(mid_tone) < self.max_chroma(
                mid_tone + tone_step_size
            )
            sufficient_chroma = (
                self.max_chroma(mid_tone) >= self.requested_chroma - epsilon
            )

            if sufficient_chroma:
                if abs(lower_tone - pivot_tone) < abs(upper_tone - pivot_tone):
                    upper_tone = mid_tone
                else:
                    if lower_tone == mid_tone:
                        return Hct.from_hct(self.hue, self.requested_chroma, lower_tone)
                    lower_tone = mid_tone
            else:
                if is_ascending:
                    lower_tone = mid_tone + tone_step_size
                else:
                    upper_tone = mid_tone

        return Hct.from_hct(self.hue, self.requested_chroma, lower_tone)

    def max_chroma(self, tone: int) -> float:
        if tone in self.chroma_cache:
            return self.chroma_cache[tone]

        chroma = Hct.from_hct(self.hue, self.max_chroma_value, tone).chroma
        self.chroma_cache[tone] = chroma
        return chroma


class TonalPalette:
    def __init__(self, hue, chroma, key_color):
        self.hue = hue
        self.chroma = chroma
        self.key_color = key_color
        self.cache = {}

    @staticmethod
    def from_int(argb: int):
        hct = Hct.from_int(argb)
        return TonalPalette.from_hct(hct)

    @staticmethod
    def from_hct(hct: Hct):
        return TonalPalette(hct.hue, hct.chroma, hct)

    @staticmethod
    def from_hue_and_chroma(hue: float, chroma: float):
        key_color = KeyColor(hue, chroma).create()
        return TonalPalette(hue, chroma, key_color)

    def tone(self, tone: float) -> int:
        argb = self.cache.get(tone)
        if argb is None:
            argb = Hct.from_hct(self.hue, self.chroma, tone).to_int()
            self.cache[tone] = argb
        return rgba_from_argb(argb)

    def get_hct(self, tone: float) -> Hct:
        return Hct.from_int(argb_from_rgb(*self.tone(tone)))
