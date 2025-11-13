from materialyoucolor.palettes.tonal_palette import TonalPalette


class CorePalettes:
    def __init__(
        self,
        primary: TonalPalette,
        secondary: TonalPalette,
        tertiary: TonalPalette,
        neutral: TonalPalette,
        neutral_variant: TonalPalette,
    ):
        self.primary = primary
        self.secondary = secondary
        self.tertiary = tertiary
        self.neutral = neutral
        self.neutral_variant = neutral_variant
