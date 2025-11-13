from materialyoucolor.hct.hct import Hct


class KeyColor:
    def __init__(self, hue: float, requested_chroma: float):
        self.chroma_cache = {}
        self.max_chroma_value = 200.0
        self.hue = hue
        self.requested_chroma = requested_chroma

    def create(self) -> Hct:
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
                        return Hct.from_hct(
                            self.hue, self.requested_chroma, float(lower_tone)
                        )
                    lower_tone = mid_tone
            else:
                if is_ascending:
                    lower_tone = mid_tone + tone_step_size
                else:
                    upper_tone = mid_tone

        return Hct.from_hct(self.hue, self.requested_chroma, float(lower_tone))

    def max_chroma(self, tone: int) -> float:
        if tone in self.chroma_cache:
            return self.chroma_cache[tone]

        chroma = Hct.from_hct(self.hue, self.max_chroma_value, float(tone)).chroma
        self.chroma_cache[tone] = chroma
        return chroma


class TonalPalette:
    def __init__(self, hue: float, chroma: float, key_color: Hct):
        self.hue = hue
        self.chroma = chroma
        self.key_color = key_color
        self.cache = {}

    @staticmethod
    def from_int(argb: int) -> "TonalPalette":
        hct = Hct.from_int(argb)
        return TonalPalette.from_hct(hct)

    @staticmethod
    def from_hct(hct: Hct) -> "TonalPalette":
        return TonalPalette(hct.hue, hct.chroma, hct)

    @staticmethod
    def from_hue_and_chroma(hue: float, chroma: float) -> "TonalPalette":
        key_color = KeyColor(hue, chroma).create()
        return TonalPalette(hue, chroma, key_color)

    def tone(self, tone: float) -> int:
        argb = self.cache.get(tone)
        if argb is None:
            if tone == 99 and Hct.is_yellow(self.hue):
                argb = self.average_argb(self.tone(98), self.tone(100))
            else:
                argb = Hct.from_hct(self.hue, self.chroma, tone).to_int()
            self.cache[tone] = argb
        return argb

    def get_hct(self, tone: float) -> Hct:
        return Hct.from_int(self.tone(tone))

    def average_argb(self, argb1: int, argb2: int) -> int:
        red1 = (argb1 >> 16) & 0xFF
        green1 = (argb1 >> 8) & 0xFF
        blue1 = argb1 & 0xFF
        red2 = (argb2 >> 16) & 0xFF
        green2 = (argb2 >> 8) & 0xFF
        blue2 = argb2 & 0xFF
        red = round((red1 + red2) / 2)
        green = round((green1 + green2) / 2)
        blue = round((blue1 + blue2) / 2)
        return (
            (0xFF << 24) | ((red & 0xFF) << 16) | ((green & 0xFF) << 8) | (blue & 0xFF)
        )
