from materialyoucolor.hct.hct import Hct
from collections import OrderedDict
from materialyoucolor.utils.string_utils import hexFromArgb
from materialyoucolor.utils.color_utils import redFromArgb, greenFromArgb, blueFromArgb


class TonalPalette:
    def __init__(self, hue, chroma):
        self.hue = hue
        self.chroma = chroma
        self.cache = OrderedDict()

    @staticmethod
    def fromInt(argb):
        hct = Hct.fromInt(argb)
        return TonalPalette.fromHueAndChroma(hct.hue, hct.chroma)

    @staticmethod
    def fromHueAndChroma(hue, chroma):
        return TonalPalette(hue, chroma)

    def tone(self, tone):
        argb = None
        if tone not in self.cache.keys():
            argb = Hct.fromHct(self.hue, self.chroma, tone).toInt()
            self.cache[tone] = argb
        else:
            argb = self.cache[tone]
        r = redFromArgb(argb)
        g = greenFromArgb(argb)
        b = blueFromArgb(argb)
        return [r, g, b]
