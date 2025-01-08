from materialyoucolor.scheme.dynamic_scheme import DynamicSchemeOptions, DynamicScheme
from materialyoucolor.scheme.variant import Variant
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.utils.math_utils import sanitize_degrees_double


class SchemeFruitSalad(DynamicScheme):
    def __init__(self, source_color_hct, is_dark, contrast_level):
        super().__init__(
            DynamicSchemeOptions(
                source_color_hct=source_color_hct,
                variant=Variant.FRUIT_SALAD,
                contrast_level=contrast_level,
                is_dark=is_dark,
                primary_palette=TonalPalette.from_hue_and_chroma(
                    sanitize_degrees_double(source_color_hct.hue - 50.0), 48.0
                ),
                secondary_palette=TonalPalette.from_hue_and_chroma(
                    sanitize_degrees_double(source_color_hct.hue - 50.0), 36.0
                ),
                tertiary_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, 36.0
                ),
                neutral_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, 10.0
                ),
                neutral_variant_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, 16.0
                ),
            )
        )
