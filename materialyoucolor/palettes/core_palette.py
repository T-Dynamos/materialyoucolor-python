from materialyoucolor.hct.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette


class CorePaletteColors:
    def __init__(self, primary, secondary, tertiary, neutral, neutral_variant, error):
        self.primary = primary
        self.secondary = secondary
        self.tertiary = tertiary
        self.neutral = neutral
        self.neutral_variant = neutral_variant
        self.error = error


class CorePalette:
    def __init__(self):
        self.a1 = None
        self.a2 = None
        self.a3 = None
        self.n1 = None
        self.n2 = None
        self.error = None

    @staticmethod
    def of(argb: int):
        return CorePalette._create_core_palette(argb, False)

    @staticmethod
    def content_of(argb: int):
        return CorePalette._create_core_palette(argb, True)

    @staticmethod
    def from_colors(colors: CorePaletteColors):
        return CorePalette._create_palette_from_colors(False, colors)

    @staticmethod
    def content_from_colors(colors: CorePaletteColors):
        return CorePalette._create_palette_from_colors(True, colors)

    @staticmethod
    def _create_palette_from_colors(content: bool, colors: CorePaletteColors):
        palette = CorePalette()
        if colors.secondary:
            p = CorePalette._create_core_palette(colors.secondary, content)
            palette.a2 = p.a1
        if colors.tertiary:
            p = CorePalette._create_core_palette(colors.tertiary, content)
            palette.a3 = p.a1
        if colors.error:
            p = CorePalette._create_core_palette(colors.error, content)
            palette.error = p.a1
        if colors.neutral:
            p = CorePalette._create_core_palette(colors.neutral, content)
            palette.n1 = p.n1
        if colors.neutral_variant:
            p = CorePalette._create_core_palette(colors.neutral_variant, content)
            palette.n2 = p.n2
        return palette

    @staticmethod
    def _create_core_palette(argb: int, is_content: bool):
        hct = Hct.from_int(argb)
        hue = hct.hue
        chroma = hct.chroma
        palette = CorePalette()
        if is_content:
            palette.a1 = TonalPalette.from_hue_and_chroma(hue, chroma)
            palette.a2 = TonalPalette.from_hue_and_chroma(hue, chroma / 3)
            palette.a3 = TonalPalette.from_hue_and_chroma(hue + 60, chroma / 2)
            palette.n1 = TonalPalette.from_hue_and_chroma(hue, min(chroma / 12, 4))
            palette.n2 = TonalPalette.from_hue_and_chroma(hue, min(chroma / 6, 8))
        else:
            palette.a1 = TonalPalette.from_hue_and_chroma(hue, max(48, chroma))
            palette.a2 = TonalPalette.from_hue_and_chroma(hue, 16)
            palette.a3 = TonalPalette.from_hue_and_chroma(hue + 60, 24)
            palette.n1 = TonalPalette.from_hue_and_chroma(hue, 4)
            palette.n2 = TonalPalette.from_hue_and_chroma(hue, 8)
        palette.error = TonalPalette.from_hue_and_chroma(25, 84)
        return palette
