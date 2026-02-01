from typing import Optional

from materialyoucolor.hct.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette


class CorePaletteColors:
    def __init__(
        self,
        primary: int,
        secondary: Optional[int] = None,
        tertiary: Optional[int] = None,
        neutral: Optional[int] = None,
        neutral_variant: Optional[int] = None,
        error: Optional[int] = None,
    ):
        self.primary = primary
        self.secondary = secondary
        self.tertiary = tertiary
        self.neutral = neutral
        self.neutral_variant = neutral_variant
        self.error = error


class CorePalette:
    def __init__(self, argb: int, is_content: bool):
        hct = Hct.from_int(argb)
        hue = hct.hue
        chroma = hct.chroma
        if is_content:
            self.a1 = TonalPalette.from_hue_and_chroma(hue, chroma)
            self.a2 = TonalPalette.from_hue_and_chroma(hue, chroma / 3)
            self.a3 = TonalPalette.from_hue_and_chroma(hue + 60, chroma / 2)
            self.n1 = TonalPalette.from_hue_and_chroma(hue, min(chroma / 12, 4))
            self.n2 = TonalPalette.from_hue_and_chroma(hue, min(chroma / 6, 8))
        else:
            self.a1 = TonalPalette.from_hue_and_chroma(hue, max(48, chroma))
            self.a2 = TonalPalette.from_hue_and_chroma(hue, 16)
            self.a3 = TonalPalette.from_hue_and_chroma(hue + 60, 24)
            self.n1 = TonalPalette.from_hue_and_chroma(hue, 4)
            self.n2 = TonalPalette.from_hue_and_chroma(hue, 8)
        self.error = TonalPalette.from_hue_and_chroma(25, 84)

    @staticmethod
    def of(argb: int) -> "CorePalette":
        return CorePalette(argb, False)

    @staticmethod
    def content_of(argb: int) -> "CorePalette":
        return CorePalette(argb, True)

    @staticmethod
    def from_colors(colors: CorePaletteColors) -> "CorePalette":
        return CorePalette._create_palette_from_colors(False, colors)

    @staticmethod
    def content_from_colors(colors: CorePaletteColors) -> "CorePalette":
        return CorePalette._create_palette_from_colors(True, colors)

    @staticmethod
    def _create_palette_from_colors(
        content: bool, colors: CorePaletteColors
    ) -> "CorePalette":
        palette = CorePalette(colors.primary, content)
        if colors.secondary:
            p = CorePalette(colors.secondary, content)
            palette.a2 = p.a1
        if colors.tertiary:
            p = CorePalette(colors.tertiary, content)
            palette.a3 = p.a1
        if colors.error:
            p = CorePalette(colors.error, content)
            palette.error = p.a1
        if colors.neutral:
            p = CorePalette(colors.neutral, content)
            palette.n1 = p.n1
        if colors.neutral_variant:
            p = CorePalette(colors.neutral_variant, content)
            palette.n2 = p.n2
        return palette
