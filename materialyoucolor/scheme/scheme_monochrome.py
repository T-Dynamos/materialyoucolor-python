from materialyoucolor.scheme.dynamic_scheme import DynamicSchemeOptions, DynamicScheme
from materialyoucolor.scheme.variant import Variant
from materialyoucolor.palettes.tonal_palette import TonalPalette


class SchemeMonochrome(DynamicScheme):
    def __init__(self, source_color_hct, is_dark, contrast_level):
        super().__init__(
            DynamicSchemeOptions(
                source_color_argb=source_color_hct.to_int(),
                variant=Variant.MONOCHROME,
                contrast_level=contrast_level,
                is_dark=is_dark,
                primary_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, 0.0
                ),
                secondary_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, 0.0
                ),
                tertiary_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, 0.0
                ),
                neutral_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, 0.0
                ),
                neutral_variant_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, 0.0
                ),
            )
        )
