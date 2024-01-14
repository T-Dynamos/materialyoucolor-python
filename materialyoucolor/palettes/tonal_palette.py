from materialyoucolor.hct import Hct
from materialyoucolor.utils.color_utils import rgba_from_argb
from materialyoucolor.utils.color_utils import argb_from_rgb


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
        return TonalPalette(hue, chroma, TonalPalette.create_key_color(hue, chroma))

    @staticmethod
    def create_key_color(hue: float, chroma: float) -> Hct:
        start_tone = 50.0
        smallest_delta_hct = Hct.from_hct(hue, chroma, start_tone)
        smallest_delta = abs(smallest_delta_hct.chroma - chroma)

        for delta in range(1, 50):
            if round(chroma) == round(smallest_delta_hct.chroma):
                return smallest_delta_hct

            hct_add = Hct.from_hct(hue, chroma, start_tone + delta)
            hct_add_delta = abs(hct_add.chroma - chroma)
            if hct_add_delta < smallest_delta:
                smallest_delta = hct_add_delta
                smallest_delta_hct = hct_add

            hct_subtract = Hct.from_hct(hue, chroma, start_tone - delta)
            hct_subtract_delta = abs(hct_subtract.chroma - chroma)
            if hct_subtract_delta < smallest_delta:
                smallest_delta = hct_subtract_delta
                smallest_delta_hct = hct_subtract

        return smallest_delta_hct

    def tone(self, tone: float) -> int:
        argb = self.cache.get(tone)
        if argb is None:
            argb = Hct.from_hct(self.hue, self.chroma, tone).to_int()
            self.cache[tone] = argb
        return rgba_from_argb(argb)

    def get_hct(self, tone: float) -> Hct:
        return Hct.from_int(argb_from_rgb(*self.tone(tone)))
