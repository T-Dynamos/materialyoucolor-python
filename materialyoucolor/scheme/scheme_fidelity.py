from materialyoucolor.dislike.dislike_analyzer import DislikeAnalyzer
from materialyoucolor.temperature.temperature_cache import TemperatureCache
from materialyoucolor.scheme.dynamic_scheme import DynamicSchemeOptions, DynamicScheme
from materialyoucolor.scheme.variant import Variant
from materialyoucolor.palettes.tonal_palette import TonalPalette


class SchemeFidelity(DynamicScheme):
    def __init__(self, source_color_hct, is_dark, contrast_level):
        super().__init__(
            DynamicSchemeOptions(
                source_color_hct=source_color_hct,
                variant=Variant.FIDELITY,
                contrast_level=contrast_level,
                is_dark=is_dark,
                primary_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, source_color_hct.chroma
                ),
                secondary_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue,
                    max(source_color_hct.chroma - 32.0, source_color_hct.chroma * 0.5),
                ),
                tertiary_palette=TonalPalette.from_int(
                    DislikeAnalyzer.fix_if_disliked(
                        TemperatureCache(source_color_hct).complement()
                    ).to_int()
                ),
                neutral_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, source_color_hct.chroma / 8.0
                ),
                neutral_variant_palette=TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, source_color_hct.chroma / 8.0 + 4.0
                ),
            )
        )
