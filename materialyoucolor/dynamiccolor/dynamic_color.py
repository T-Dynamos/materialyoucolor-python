from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional

from materialyoucolor.contrast.contrast import Contrast
from materialyoucolor.dynamiccolor.color_spec import (
    SpecVersion,
    get_color_calculation_delegate,
)
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve
from materialyoucolor.dynamiccolor.tone_delta_pair import ToneDeltaPair
from materialyoucolor.hct.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.utils.color_utils import hex_from_argb, rgba_from_argb


@dataclass
class FromPaletteOptions:
    name: str = ""
    palette: Callable[[DynamicScheme], TonalPalette] = None
    tone: Callable[[DynamicScheme], float] = None
    chroma_multiplier: Optional[Callable[[DynamicScheme], float]] = None
    is_background: bool = False
    background: Optional[Callable[[DynamicScheme], "DynamicColor"]] = None
    second_background: Optional[Callable[[DynamicScheme], "DynamicColor"]] = None
    contrast_curve: Optional[Callable[[DynamicScheme], ContrastCurve]] = None
    tone_delta_pair: Optional[Callable[[DynamicScheme], ToneDeltaPair]] = None


def validate_extended_color(
    original_color: "DynamicColor",
    spec_version: SpecVersion,
    extended_color: "DynamicColor",
):
    if original_color.name != extended_color.name:
        raise ValueError(
            f"Attempting to extend color {original_color.name} with color {extended_color.name} "
            f"of different name for spec version {spec_version}."
        )
    if original_color.is_background != extended_color.is_background:
        raise ValueError(
            f"Attempting to extend color {original_color.name} as a "
            f"{'background' if original_color.is_background else 'foreground'} with color {extended_color.name} as a "
            f"{'background' if extended_color.is_background else 'foreground'} for spec version {spec_version}."
        )


def extend_spec_version(original, spec, extended):
    validate_extended_color(original, spec, extended)

    def choose(s, _ext=extended, _orig=original, _spec=spec):
        return _ext if s.spec_version == _spec else _orig

    return DynamicColor(
        name=original.name,
        is_background=original.is_background,
        palette=lambda s: choose(s).palette(s),
        tone=lambda s: (
            choose(s).tone(s) if choose(s).tone is not None else original.tone(s)
        ),
        chroma_multiplier=lambda s: (
            choose(s).chroma_multiplier(s) if choose(s).chroma_multiplier else 1.0
        ),
        background=lambda s: (
            choose(s).background(s) if choose(s).background else None
        ),
        second_background=lambda s: (
            choose(s).second_background(s) if choose(s).second_background else None
        ),
        contrast_curve=lambda s: (
            choose(s).contrast_curve(s) if choose(s).contrast_curve else None
        ),
        tone_delta_pair=lambda s: (
            choose(s).tone_delta_pair(s) if choose(s).tone_delta_pair else None
        ),
    )


class DynamicColor(FromPaletteOptions):
    hct_cache = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hct_cache = {}
        if not self.background and self.second_background:
            raise ValueError(
                f"Color {self.name} has second_background defined, but background is not defined."
            )
        if not self.background and self.contrast_curve:
            raise ValueError(
                f"Color {self.name} has contrast_curve defined, but background is not defined."
            )
        if self.background and not self.contrast_curve:
            raise ValueError(
                f"Color {self.name} has background defined, but contrast_curve is not defined."
            )

    @classmethod
    def from_palette(cls, *args, **kwargs) -> "DynamicColor":
        if "tone" not in kwargs or kwargs.get("tone") is None:
            kwargs["tone"] = cls.get_initial_tone_from_background(
                kwargs.get("background")
            )
        return cls(*args, **kwargs)

    @staticmethod
    def get_initial_tone_from_background(
        background: Optional[Callable[[DynamicScheme], "DynamicColor"]] = None,
    ) -> Callable[[DynamicScheme], float]:
        if background is None:
            return lambda s: 50
        return lambda s: background(s).get_tone(s) if background(s) else 50

    def clone(self) -> "DynamicColor":
        return DynamicColor.from_palette(
            name=self.name,
            palette=self.palette,
            tone=self.tone,
            is_background=self.is_background,
            chroma_multiplier=self.chroma_multiplier,
            background=self.background,
            second_background=self.second_background,
            contrast_curve=self.contrast_curve,
            tone_delta_pair=self.tone_delta_pair,
        )

    def clear_cache(self):
        self.hct_cache.clear()

    def get_argb(self, scheme: DynamicScheme) -> int:
        return self.get_hct(scheme).to_int()

    def get_hex(self, scheme: DynamicScheme) -> str:
        return hex_from_argb(self.get_hct(scheme).to_int())

    def get_rgba(self, scheme: DynamicScheme) -> list[int]:
        return rgba_from_argb(self.get_hct(scheme).to_int())

    def get_hct(self, scheme: DynamicScheme) -> Hct:
        cached_answer = self.hct_cache.get(scheme)
        if cached_answer is not None:
            return cached_answer

        answer = get_color_calculation_delegate(scheme.spec_version).get_hct(
            scheme, self
        )
        if len(self.hct_cache) > 4:
            self.hct_cache.clear()
        self.hct_cache[scheme] = answer
        return answer

    def get_tone(self, scheme: DynamicScheme) -> float:
        return get_color_calculation_delegate(scheme.spec_version).get_tone(
            scheme, self
        )

    @staticmethod
    def foreground_tone(bg_tone: float, ratio: float) -> float:
        lighter_tone = Contrast.lighter_unsafe(bg_tone, ratio)
        darker_tone = Contrast.darker_unsafe(bg_tone, ratio)
        lighter_ratio = Contrast.ratio_of_tones(lighter_tone, bg_tone)
        darker_ratio = Contrast.ratio_of_tones(darker_tone, bg_tone)
        prefer_lighter = DynamicColor.tone_prefers_light_foreground(bg_tone)

        if prefer_lighter:
            negligible_difference = (
                abs(lighter_ratio - darker_ratio) < 0.1
                and lighter_ratio < ratio
                and darker_ratio < ratio
            )
            return (
                lighter_tone
                if lighter_ratio >= ratio
                or lighter_ratio >= darker_ratio
                or negligible_difference
                else darker_tone
            )
        else:
            return (
                darker_tone
                if darker_ratio >= ratio or darker_ratio >= lighter_ratio
                else lighter_tone
            )

    @staticmethod
    def tone_prefers_light_foreground(tone: float) -> bool:
        return round(tone) < 60.0

    @staticmethod
    def tone_allows_light_foreground(tone: float) -> bool:
        return round(tone) <= 49.0

    @staticmethod
    def enable_light_foreground(tone: float) -> float:
        if DynamicColor.tone_prefers_light_foreground(
            tone
        ) and not DynamicColor.tone_allows_light_foreground(tone):
            return 49.0
        return tone
