from materialyoucolor.scheme.dynamic_scheme import DynamicSchemeOptions, DynamicScheme
from materialyoucolor.scheme.variant import Variant
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.utils.math_utils import sanitize_degrees_double


class SchemeExpressive(DynamicScheme):
    hues = [0.0, 21.0, 51.0, 121.0, 151.0, 191.0, 271.0, 321.0, 360.0]
    secondary_rotations = [45.0, 95.0, 45.0, 20.0, 45.0, 90.0, 45.0, 45.0, 45.0]
    tertiary_rotations = [120.0, 120.0, 20.0, 45.0, 20.0, 15.0, 20.0, 120.0, 120.0]

    def __init__(self, source_color_hct, is_dark, contrast_level):
        super().__init__(
            DynamicSchemeOptions(
                source_color_argb=source_color_hct.to_int(),
                variant=Variant.EXPRESSIVE,
                contrast_level=contrast_level,
                is_dark=is_dark,
                primary_palette=TonalPalette.from_hue_and_chroma(
                    sanitize_degrees_double(source_color_hct.hue + 240.0), 40.0
                ),
                secondary_palette=TonalPalette.from_hue_and_chroma(
                    DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        SchemeExpressive.hues,
                        SchemeExpressive.secondary_rotations,
                    ),
                    24.0,
                ),
                tertiary_palette=TonalPalette.from_hue_and_chroma(
                    DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        SchemeExpressive.hues,
                        SchemeExpressive.tertiary_rotations,
                    ),
                    32.0,
                ),
                neutral_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue + 15, 8.0
                ),
                neutral_variant_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue + 15, 12.0
                ),
            )
        )
