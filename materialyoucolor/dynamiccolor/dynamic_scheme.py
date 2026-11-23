from __future__ import annotations

from typing import Literal

from materialyoucolor.dislike.dislike_analyzer import DislikeAnalyzer
from materialyoucolor.dynamiccolor.dynamic_color import DynamicColor
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.temperature.temperature_cache import TemperatureCache
from materialyoucolor.utils.math_utils import sanitize_degrees_double, clamp_double

SpecVersion = Literal["2021", "2025", "2026"]
Platform = Literal["phone", "watch"]


class DynamicSchemePalettesDelegate:
    def get_primary_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        raise NotImplementedError

    def get_secondary_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        raise NotImplementedError

    def get_tertiary_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        raise NotImplementedError

    def get_neutral_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        raise NotImplementedError

    def get_neutral_variant_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        raise NotImplementedError

    def get_error_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette | None:
        raise NotImplementedError


class DynamicScheme:
    DEFAULT_SPEC_VERSION: SpecVersion = "2025"
    DEFAULT_PLATFORM: Platform = "phone"

    def __init__(
        self,
        source_color_hct: Hct | list[Hct] | None = None,
        variant: Variant = Variant.TONAL_SPOT,
        contrast_level: float = 0.0,
        is_dark: bool = False,
        platform: Platform = "phone",
        spec_version: SpecVersion = "2021",
        primary_palette: TonalPalette = None,
        secondary_palette: TonalPalette = None,
        tertiary_palette: TonalPalette = None,
        neutral_palette: TonalPalette = None,
        neutral_variant_palette: TonalPalette = None,
        error_palette: TonalPalette = None,
        source_color_hcts: list[Hct] | None = None,
    ):
        if source_color_hcts:
            if len(source_color_hcts) == 0:
                raise ValueError("source_color_hcts cannot be empty")
            self.source_color_hct = source_color_hcts[0]
            self.source_color_hcts = list(source_color_hcts)
        elif source_color_hct is not None:
            if isinstance(source_color_hct, (list, tuple)):
                if len(source_color_hct) == 0:
                    raise ValueError("source_color_hct list cannot be empty")
                self.source_color_hct = source_color_hct[0]
                self.source_color_hcts = list(source_color_hct)
            else:
                self.source_color_hct = source_color_hct
                self.source_color_hcts = [source_color_hct]
        else:
            raise ValueError("source_color_hct or source_color_hcts required")

        self.source_color_argb = self.source_color_hct.to_int()
        self.variant = variant
        self.contrast_level = contrast_level
        self.is_dark = is_dark
        self.platform = platform
        self.spec_version = self._maybe_fallback_spec_version(
            spec_version, variant, platform
        )

        spec = get_spec(self.spec_version)
        self.primary_palette = primary_palette or spec.get_primary_palette(
            self.variant,
            self.source_color_hct,
            self.is_dark,
            self.platform,
            self.contrast_level,
        )
        self.secondary_palette = secondary_palette or spec.get_secondary_palette(
            self.variant,
            self.source_color_hct,
            self.is_dark,
            self.platform,
            self.contrast_level,
        )
        self.tertiary_palette = tertiary_palette or spec.get_tertiary_palette(
            self.variant,
            self.source_color_hct,
            self.is_dark,
            self.platform,
            self.contrast_level,
        )
        self.neutral_palette = neutral_palette or spec.get_neutral_palette(
            self.variant,
            self.source_color_hct,
            self.is_dark,
            self.platform,
            self.contrast_level,
        )
        self.neutral_variant_palette = (
            neutral_variant_palette
            or spec.get_neutral_variant_palette(
                self.variant,
                self.source_color_hct,
                self.is_dark,
                self.platform,
                self.contrast_level,
            )
        )
        self.error_palette = (
            error_palette
            or spec.get_error_palette(
                self.variant,
                self.source_color_hct,
                self.is_dark,
                self.platform,
                self.contrast_level,
            )
            or TonalPalette.from_hue_and_chroma(25.0, 84.0)
        )

    @staticmethod
    def _maybe_fallback_spec_version(
        spec_version: SpecVersion, variant: Variant, platform: Platform = "phone"
    ) -> SpecVersion:
        if variant == Variant.CMF:
            return spec_version
        if (
            variant in [
                Variant.EXPRESSIVE,
                Variant.VIBRANT,
                Variant.TONAL_SPOT,
                Variant.NEUTRAL,
            ]
            or (platform == "watch" and variant == Variant.CONTENT)
        ):
            return "2025" if spec_version == "2026" else spec_version
        return "2021"

    def __str__(self):
        return (
            f"Scheme: "
            f"variant={self.variant.name}, "
            f"mode={'dark' if self.is_dark else 'light'}, "
            f"platform={self.platform}, "
            f"contrastLevel={self.contrast_level:.1f}, "
            f"seed={self.source_color_hct}, "
            f"specVersion={self.spec_version}"
        )

    @staticmethod
    def get_piecewise_hue(
        source_color_hct: Hct, hue_breakpoints: list[float], hues: list[float]
    ) -> float:
        size = min(len(hue_breakpoints) - 1, len(hues))
        source_hue = source_color_hct.hue
        for i in range(size):
            if source_hue >= hue_breakpoints[i] and source_hue < hue_breakpoints[i + 1]:
                return sanitize_degrees_double(hues[i])
        # No condition matched, return the source hue.
        return source_hue

    @staticmethod
    def get_rotated_hue(
        source_color_hct: Hct, hue_breakpoints: list[float], rotations: list[float]
    ) -> float:
        rotation = DynamicScheme.get_piecewise_hue(
            source_color_hct, hue_breakpoints, rotations
        )
        if min(len(hue_breakpoints) - 1, len(rotations)) <= 0:
            # No condition matched, return the source hue.
            rotation = 0
        return sanitize_degrees_double(source_color_hct.hue + rotation)

    def get_argb(self, dynamic_color: DynamicColor) -> int:
        return dynamic_color.get_argb(self)

    def get_hct(self, dynamic_color: DynamicColor) -> Hct:
        return dynamic_color.get_hct(self)


class DynamicSchemePalettesDelegateImpl2021(DynamicSchemePalettesDelegate):
    def get_primary_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if variant == Variant.CONTENT or variant == Variant.FIDELITY:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, source_color_hct.chroma
            )
        if variant == Variant.FRUIT_SALAD:
            return TonalPalette.from_hue_and_chroma(
                sanitize_degrees_double(source_color_hct.hue - 50.0), 48.0
            )
        if variant == Variant.MONOCHROME:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 0.0)
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 12.0)
        if variant == Variant.RAINBOW:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 48.0)
        if variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 36.0)
        if variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                sanitize_degrees_double(source_color_hct.hue + 240), 40
            )
        if variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 200.0)
        raise ValueError(f"Unsupported variant: {variant}")

    def get_secondary_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if variant == Variant.CONTENT or variant == Variant.FIDELITY:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue,
                max(source_color_hct.chroma - 32.0, source_color_hct.chroma * 0.5),
            )
        if variant == Variant.FRUIT_SALAD:
            return TonalPalette.from_hue_and_chroma(
                sanitize_degrees_double(source_color_hct.hue - 50.0), 36.0
            )
        if variant == Variant.MONOCHROME:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 0.0)
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 8.0)
        if variant == Variant.RAINBOW:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 16.0)
        if variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 16.0)
        if variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                DynamicScheme.get_rotated_hue(
                    source_color_hct,
                    [0, 21, 51, 121, 151, 191, 271, 321, 360],
                    [45, 95, 45, 20, 45, 90, 45, 45, 45],
                ),
                24.0,
            )
        if variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(
                DynamicScheme.get_rotated_hue(
                    source_color_hct,
                    [0, 41, 61, 101, 131, 181, 251, 301, 360],
                    [18, 15, 10, 12, 15, 18, 15, 12, 12],
                ),
                24.0,
            )
        raise ValueError(f"Unsupported variant: {variant}")

    def get_tertiary_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if variant == Variant.CONTENT:
            return TonalPalette.from_hct(
                DislikeAnalyzer.fix_if_disliked(
                    TemperatureCache(source_color_hct).analogous(count=3, divisions=6)[
                        2
                    ]
                )
            )
        if variant == Variant.FIDELITY:
            return TonalPalette.from_hct(
                DislikeAnalyzer.fix_if_disliked(
                    TemperatureCache(source_color_hct).complement
                )
            )
        if variant == Variant.FRUIT_SALAD:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 36.0)
        if variant == Variant.MONOCHROME:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 0.0)
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 16.0)
        if variant == Variant.RAINBOW or variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(
                sanitize_degrees_double(source_color_hct.hue + 60.0), 24.0
            )
        if variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                DynamicScheme.get_rotated_hue(
                    source_color_hct,
                    [0, 21, 51, 121, 151, 191, 271, 321, 360],
                    [120, 120, 20, 45, 20, 15, 20, 120, 120],
                ),
                32.0,
            )
        if variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(
                DynamicScheme.get_rotated_hue(
                    source_color_hct,
                    [0, 41, 61, 101, 131, 181, 251, 301, 360],
                    [35, 30, 20, 25, 30, 35, 30, 25, 25],
                ),
                32.0,
            )
        raise ValueError(f"Unsupported variant: {variant}")

    def get_neutral_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if variant == Variant.CONTENT or variant == Variant.FIDELITY:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, source_color_hct.chroma / 8.0
            )
        if variant == Variant.FRUIT_SALAD:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 10.0)
        if variant == Variant.MONOCHROME:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 0.0)
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 2.0)
        if variant == Variant.RAINBOW:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 0.0)
        if variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 6.0)
        if variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                sanitize_degrees_double(source_color_hct.hue + 15), 8
            )
        if variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 10)
        raise ValueError(f"Unsupported variant: {variant}")

    def get_neutral_variant_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if variant == Variant.CONTENT:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, (source_color_hct.chroma / 8.0) + 4.0
            )
        if variant == Variant.FIDELITY:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, (source_color_hct.chroma / 8.0) + 4.0
            )
        if variant == Variant.FRUIT_SALAD:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 16.0)
        if variant == Variant.MONOCHROME:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 0.0)
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 2.0)
        if variant == Variant.RAINBOW:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 0.0)
        if variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 8.0)
        if variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                sanitize_degrees_double(source_color_hct.hue + 15), 12
            )
        if variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 12)
        raise ValueError(f"Unsupported variant: {variant}")

    def get_error_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette | None:
        return None


class DynamicSchemePalettesDelegateImpl2025(DynamicSchemePalettesDelegateImpl2021):
    def get_primary_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue,
                (
                    (12 if Hct.is_blue(source_color_hct.hue) else 8)
                    if platform == "phone"
                    else (
                        16
                        if DynamicSchemePalettesDelegateImpl2025._is_watch_blue_hue(
                            source_color_hct
                        )
                        else 12
                    )
                ),
            )
        elif variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, 26 if platform == "phone" and is_dark else 32
            )
        elif variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue,
                (36 if is_dark else 48) if platform == "phone" else 40,
            )
        elif variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, 74 if platform == "phone" else 48
            )
        elif variant == Variant.CONTENT:
            return (
                TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue, source_color_hct.chroma
                )
                if platform == "watch"
                else super().get_primary_palette(
                    variant, source_color_hct, is_dark, platform, contrast_level
                )
            )
        return super().get_primary_palette(
            variant, source_color_hct, is_dark, platform, contrast_level
        )

    def get_secondary_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue,
                (
                    (6 if Hct.is_blue(source_color_hct.hue) else 4)
                    if platform == "phone"
                    else (
                        10
                        if DynamicSchemePalettesDelegateImpl2025._is_watch_blue_hue(
                            source_color_hct
                        )
                        else 6
                    )
                ),
            )
        elif variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(source_color_hct.hue, 16)
        elif variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                (
                    DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 21, 51, 121, 151, 191, 271, 321, 360],
                        [204, 175, 155, 150, 204, 260, 204, 204, 204],
                    )
                    if platform == "watch"
                    else DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 105, 140, 204, 253, 278, 300, 333, 360],
                        [-160, 155, -100, 96, -96, -156, -165, -160],
                    )
                ),
                (16 if is_dark else 24) if platform == "phone" else 24,
            )
        elif variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(
                (
                    DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 41, 61, 101, 131, 181, 251, 301, 360],
                        [-14, 0, 355, 357, 0, 3, 10, 331, 331],
                    )
                    if platform == "watch"
                    else DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 38, 105, 140, 333, 360],
                        [-14, 10, -14, 10, -14],
                    )
                ),
                56 if platform == "phone" else 36,
            )
        elif variant == Variant.CONTENT:
            return (
                TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue,
                    clamp_double(16.0, 36.0, source_color_hct.chroma * 0.5),
                )
                if platform == "watch"
                else super().get_secondary_palette(
                    variant, source_color_hct, is_dark, platform, contrast_level
                )
            )
        return super().get_secondary_palette(
            variant, source_color_hct, is_dark, platform, contrast_level
        )

    def get_tertiary_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(
                (
                    DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 41, 61, 101, 131, 181, 250, 270, 360],
                        [25, 25, 26, 25, -39, 25, 28, 25, 25],
                    )
                    if platform == "watch"
                    else DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 38, 105, 161, 204, 278, 333, 360],
                        [-32, 26, 10, -39, 24, -15, -32],
                    )
                ),
                20 if platform == "phone" else 36,
            )
        elif variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(
                (
                    DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 40, 101, 210, 301, 360],
                        [-32, 32, -32, 32, -32, -32],
                    )
                    if platform == "watch"
                    else DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 20, 71, 161, 333, 360],
                        [-40, 48, -32, 40, -32],
                    )
                ),
                28 if platform == "phone" else 32,
            )
        elif variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                (
                    DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 21, 51, 121, 151, 191, 271, 321, 360],
                        [200, 200, 160, 169, 200, 220, 200, 200, 200],
                    )
                    if platform == "watch"
                    else DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 105, 140, 204, 253, 278, 300, 333, 360],
                        [-165, 160, -105, 101, -101, -160, -170, -165],
                    )
                ),
                48,
            )
        elif variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(
                (
                    DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 41, 61, 101, 131, 181, 251, 301, 360],
                        [-72, 55, 45, 50, 55, 50, 62, 303, 303],
                    )
                    if platform == "watch"
                    else DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 38, 71, 105, 140, 161, 253, 333, 360],
                        [-72, 35, 24, -24, 62, 50, 62, -72],
                    )
                ),
                56 if platform == "phone" else 48,
            )
        elif variant == Variant.CONTENT:
            return (
                TonalPalette.from_hue_and_chroma(
                    DynamicScheme.get_rotated_hue(
                        source_color_hct,
                        [0, 40, 101, 210, 301, 360],
                        [-32, 32, -32, 32, -32, -32],
                    ),
                    source_color_hct.chroma,
                )
                if platform == "watch"
                else super().get_tertiary_palette(
                    variant, source_color_hct, is_dark, platform, contrast_level
                )
            )
        return super().get_tertiary_palette(
            variant, source_color_hct, is_dark, platform, contrast_level
        )

    @staticmethod
    def _is_watch_blue_hue(source_color_hct: Hct) -> bool:
        return 250 <= source_color_hct.hue <= 270

    @staticmethod
    def _get_expressive_neutral_hue(
        source_color_hct: Hct, platform: Platform = "phone"
    ) -> float:
        if platform == "watch":
            return DynamicScheme.get_rotated_hue(
                source_color_hct,
                [0, 21, 51, 121, 151, 191, 271, 321, 360],
                [0, 0, 0, 0, 0, 0, 10, 0, 0],
            )
        return DynamicScheme.get_rotated_hue(
            source_color_hct,
            [0, 71, 124, 253, 278, 300, 360],
            [10, 0, 10, 0, 10, 0],
        )

    @staticmethod
    def _get_expressive_neutral_chroma(
        source_color_hct: Hct, is_dark: bool, platform: Platform
    ) -> float:
        neutral_hue = DynamicSchemePalettesDelegateImpl2025._get_expressive_neutral_hue(
            source_color_hct, platform
        )
        return (
            ((6 if Hct.is_yellow(neutral_hue) else 14) if is_dark else 18)
            if platform == "phone"
            else 12
        )

    @staticmethod
    def _get_vibrant_neutral_hue(
        source_color_hct: Hct, platform: Platform = "phone"
    ) -> float:
        if platform == "watch":
            return DynamicScheme.get_rotated_hue(
                source_color_hct,
                [0, 41, 61, 101, 131, 181, 251, 301, 360],
                [-14, 0, 355, 357, 0, 3, 10, 331, 331],
            )
        return DynamicScheme.get_rotated_hue(
            source_color_hct, [0, 38, 105, 140, 333, 360], [-14, 10, -14, 10, -14]
        )

    @staticmethod
    def _get_vibrant_neutral_chroma(source_color_hct: Hct, platform: Platform) -> float:
        return (
            28
            if platform == "phone"
            or DynamicSchemePalettesDelegateImpl2025._is_watch_blue_hue(source_color_hct)
            else 20
        )

    def get_neutral_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, 1.4 if platform == "phone" else 6
            )
        elif variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, 5 if platform == "phone" else 10
            )
        elif variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                DynamicSchemePalettesDelegateImpl2025._get_expressive_neutral_hue(
                    source_color_hct, platform
                ),
                DynamicSchemePalettesDelegateImpl2025._get_expressive_neutral_chroma(
                    source_color_hct, is_dark, platform
                ),
            )
        elif variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(
                DynamicSchemePalettesDelegateImpl2025._get_vibrant_neutral_hue(
                    source_color_hct, platform
                ),
                DynamicSchemePalettesDelegateImpl2025._get_vibrant_neutral_chroma(
                    source_color_hct, platform
                ),
            )
        elif variant == Variant.CONTENT:
            return (
                TonalPalette.from_hue_and_chroma(
                    source_color_hct.hue,
                    clamp_double(6.0, 20.0, source_color_hct.chroma * 0.333),
                )
                if platform == "watch"
                else super().get_neutral_palette(
                    variant, source_color_hct, is_dark, platform, contrast_level
                )
            )
        return super().get_neutral_palette(
            variant, source_color_hct, is_dark, platform, contrast_level
        )

    def get_neutral_variant_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette:
        if platform == "watch":
            if variant in [
                Variant.NEUTRAL,
                Variant.TONAL_SPOT,
                Variant.EXPRESSIVE,
                Variant.VIBRANT,
                Variant.CONTENT,
            ]:
                return self.get_neutral_palette(
                    variant, source_color_hct, is_dark, platform, contrast_level
                )
            return super().get_neutral_variant_palette(
                variant, source_color_hct, is_dark, platform, contrast_level
            )
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, (1.4 if platform == "phone" else 6) * 2.2
            )
        elif variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(
                source_color_hct.hue, (5 if platform == "phone" else 10) * 1.7
            )
        elif variant == Variant.EXPRESSIVE:
            expressive_neutral_hue = (
                DynamicSchemePalettesDelegateImpl2025._get_expressive_neutral_hue(
                    source_color_hct, platform
                )
            )
            expressive_neutral_chroma = (
                DynamicSchemePalettesDelegateImpl2025._get_expressive_neutral_chroma(
                    source_color_hct, is_dark, platform
                )
            )
            return TonalPalette.from_hue_and_chroma(
                expressive_neutral_hue,
                expressive_neutral_chroma
                * (
                    1.6
                    if 105 <= expressive_neutral_hue < 125
                    else 2.3
                ),
            )
        elif variant == Variant.VIBRANT:
            vibrant_neutral_hue = (
                DynamicSchemePalettesDelegateImpl2025._get_vibrant_neutral_hue(
                    source_color_hct, platform
                )
            )
            vibrant_neutral_chroma = (
                DynamicSchemePalettesDelegateImpl2025._get_vibrant_neutral_chroma(
                    source_color_hct, platform
                )
            )
            return TonalPalette.from_hue_and_chroma(
                vibrant_neutral_hue, vibrant_neutral_chroma * 1.29
            )
        return super().get_neutral_variant_palette(
            variant, source_color_hct, is_dark, platform, contrast_level
        )

    def get_error_palette(
        self,
        variant: Variant,
        source_color_hct: Hct,
        is_dark: bool,
        platform: Platform,
        contrast_level: float,
    ) -> TonalPalette | None:
        error_hue = DynamicScheme.get_piecewise_hue(
            source_color_hct,
            [0, 3, 13, 23, 33, 43, 153, 273, 360],
            [12, 22, 32, 12, 22, 32, 22, 12],
        )
        if variant == Variant.NEUTRAL:
            return TonalPalette.from_hue_and_chroma(
                error_hue, 50 if platform == "phone" else 40
            )
        elif variant == Variant.TONAL_SPOT:
            return TonalPalette.from_hue_and_chroma(
                error_hue, 60 if platform == "phone" else 48
            )
        elif variant == Variant.EXPRESSIVE:
            return TonalPalette.from_hue_and_chroma(
                error_hue, 64 if platform == "phone" else 48
            )
        elif variant == Variant.VIBRANT:
            return TonalPalette.from_hue_and_chroma(
                error_hue, 80 if platform == "phone" else 48
            )
        elif variant == Variant.CONTENT:
            return (
                TonalPalette.from_hue_and_chroma(
                    error_hue, max(40.0, source_color_hct.chroma)
                )
                if platform == "watch"
                else super().get_error_palette(
                    variant, source_color_hct, is_dark, platform, contrast_level
                )
            )
        return super().get_error_palette(
            variant, source_color_hct, is_dark, platform, contrast_level
        )


_spec2021 = DynamicSchemePalettesDelegateImpl2021()
_spec2025 = DynamicSchemePalettesDelegateImpl2025()


def get_spec(spec_version: SpecVersion) -> DynamicSchemePalettesDelegate:
    return _spec2021 if spec_version == "2021" else _spec2025
