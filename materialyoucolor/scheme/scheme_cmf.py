from __future__ import annotations

from materialyoucolor.dynamiccolor.dynamic_scheme import (
    DynamicScheme,
    Platform,
    SpecVersion,
)
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette


class SchemeCmf(DynamicScheme):
    def __init__(
        self,
        source_color_hct: Hct | list[Hct] | None = None,
        is_dark: bool = False,
        contrast_level: float = 0.0,
        spec_version: SpecVersion = "2026",
        platform: Platform = DynamicScheme.DEFAULT_PLATFORM,
        source_color_hcts: list[Hct] | None = None,
    ):
        if spec_version != "2026":
            raise ValueError("SchemeCmf can only be used with spec version 2026.")

        source_color_or_list = (
            source_color_hcts if source_color_hcts is not None else source_color_hct
        )
        is_array = isinstance(source_color_or_list, list)
        main_source = source_color_or_list[0] if is_array else source_color_or_list
        extra_sources = source_color_or_list[1:] if is_array else []

        secondary_source = extra_sources[0] if len(extra_sources) > 0 else main_source

        primary_palette = TonalPalette.from_hue_and_chroma(
            main_source.hue, main_source.chroma
        )
        secondary_palette = TonalPalette.from_hue_and_chroma(
            main_source.hue, main_source.chroma * 0.5
        )
        tertiary_palette = (
            TonalPalette.from_hue_and_chroma(
                main_source.hue, main_source.chroma * 0.75
            )
            if main_source.to_int() == secondary_source.to_int()
            else TonalPalette.from_hue_and_chroma(
                secondary_source.hue, secondary_source.chroma
            )
        )
        neutral_palette = TonalPalette.from_hue_and_chroma(
            main_source.hue, main_source.chroma * 0.2
        )
        neutral_variant_palette = TonalPalette.from_hue_and_chroma(
            main_source.hue, main_source.chroma * 0.2
        )
        error_palette = TonalPalette.from_hue_and_chroma(
            SchemeCmf.calculate_error_hue(main_source.hue, secondary_source.hue),
            max(main_source.chroma, 50.0),
        )

        super().__init__(
            source_color_hcts=source_color_or_list
            if is_array
            else [source_color_or_list],
            variant=Variant.CMF,
            contrast_level=contrast_level,
            is_dark=is_dark,
            platform=platform,
            spec_version=spec_version,
            primary_palette=primary_palette,
            secondary_palette=secondary_palette,
            tertiary_palette=tertiary_palette,
            neutral_palette=neutral_palette,
            neutral_variant_palette=neutral_variant_palette,
            error_palette=error_palette,
        )

    @staticmethod
    def get_error_hue(primary_hue: float, tertiary_hue: float) -> float:
        if primary_hue <= 8:
            return 28 if tertiary_hue <= 24 else (16 if tertiary_hue <= 32 else 20)
        elif primary_hue <= 16:
            return 32 if tertiary_hue <= 24 else (20 if tertiary_hue <= 32 else 24)
        elif primary_hue <= 20:
            return 32 if tertiary_hue <= 28 else (24 if tertiary_hue <= 32 else 28)
        elif primary_hue <= 28:
            return 32 if tertiary_hue <= 24 else 16
        elif primary_hue <= 32:
            return 24 if tertiary_hue <= 20 else (16 if tertiary_hue <= 28 else 20)
        elif primary_hue <= 40:
            return 16 if (20 < tertiary_hue <= 28) else 24
        elif primary_hue <= 152:
            return 20 if (24 < tertiary_hue <= 36) else 32
        elif primary_hue <= 272:
            return 16 if (20 < tertiary_hue <= 28) else 24
        else:
            return 32 if (12 < tertiary_hue <= 28) else 16

    calculate_error_hue = get_error_hue
