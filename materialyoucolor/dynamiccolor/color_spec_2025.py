from typing import Optional

from materialyoucolor.dynamiccolor.color_spec_2021 import ColorSpecDelegateImpl2021
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve
from materialyoucolor.dynamiccolor.dynamic_color import (
    DynamicColor,
    extend_spec_version,
)
from materialyoucolor.dynamiccolor.dynamic_scheme import DynamicScheme
from materialyoucolor.dynamiccolor.tone_delta_pair import ToneDeltaPair
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.utils.math_utils import clamp_double


def t_max_c(
    palette: TonalPalette,
    lower_bound: float = 0,
    upper_bound: float = 100,
    chroma_multiplier: float = 1,
) -> float:
    answer = find_best_tone_for_chroma(
        palette.hue, palette.chroma * chroma_multiplier, 100, True
    )
    return clamp_double(lower_bound, upper_bound, answer)


def t_min_c(
    palette: TonalPalette, lower_bound: float = 0, upper_bound: float = 100
) -> float:
    answer = find_best_tone_for_chroma(palette.hue, palette.chroma, 0, False)
    return clamp_double(lower_bound, upper_bound, answer)


def find_best_tone_for_chroma(
    hue: float, chroma: float, tone: float, by_decreasing_tone: bool
) -> float:
    answer = tone
    best_candidate = Hct.from_hct(hue, chroma, answer)
    while best_candidate.chroma < chroma:
        if tone < 0 or tone > 100:
            break
        tone += -1.0 if by_decreasing_tone else 1.0
        new_candidate = Hct.from_hct(hue, chroma, tone)
        if best_candidate.chroma < new_candidate.chroma:
            best_candidate = new_candidate
            answer = tone
    return answer


def get_curve(default_contrast: float) -> ContrastCurve:
    if default_contrast == 1.5:
        return ContrastCurve(1.5, 1.5, 3, 5.5)
    elif default_contrast == 3:
        return ContrastCurve(3, 3, 4.5, 7)
    elif default_contrast == 4.5:
        return ContrastCurve(4.5, 4.5, 7, 11)
    elif default_contrast == 6:
        return ContrastCurve(6, 6, 7, 11)
    elif default_contrast == 7:
        return ContrastCurve(7, 7, 11, 21)
    elif default_contrast == 9:
        return ContrastCurve(9, 9, 11, 21)
    elif default_contrast == 11:
        return ContrastCurve(11, 11, 21, 21)
    elif default_contrast == 21:
        return ContrastCurve(21, 21, 21, 21)
    else:
        return ContrastCurve(default_contrast, default_contrast, 7, 21)


class ColorSpecDelegateImpl2025(ColorSpecDelegateImpl2021):
    def _surface_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.is_dark:
                return 4
            else:
                if Hct.is_yellow(s.neutral_palette.hue):
                    return 99
                elif s.variant == Variant.VIBRANT:
                    return 97
                else:
                    return 98
        else:
            return 0

    def surface(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="surface",
            palette=lambda s: s.neutral_palette,
            tone=self._surface_tone_2025,
            is_background=True,
        )
        return extend_spec_version(super().surface(), "2025", color2025)

    def _surface_dim_tone_2025(self, s: DynamicScheme) -> float:
        if s.is_dark:
            return 4
        else:
            if Hct.is_yellow(s.neutral_palette.hue):
                return 90
            elif s.variant == Variant.VIBRANT:
                return 85
            else:
                return 87

    def _surface_dim_chroma_multiplier_2025(self, s: DynamicScheme) -> float:
        if not s.is_dark:
            if s.variant == Variant.NEUTRAL:
                return 2.5
            elif s.variant == Variant.TONAL_SPOT:
                return 1.7
            elif s.variant == Variant.EXPRESSIVE:
                return 2.7 if Hct.is_yellow(s.neutral_palette.hue) else 1.75
            elif s.variant == Variant.VIBRANT:
                return 1.36
        return 1.0

    def surfaceDim(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="surfaceDim",
            palette=lambda s: s.neutral_palette,
            tone=self._surface_dim_tone_2025,
            is_background=True,
            chroma_multiplier=self._surface_dim_chroma_multiplier_2025,
        )
        return extend_spec_version(super().surfaceDim(), "2025", color2025)

    def _surface_bright_tone_2025(self, s: DynamicScheme) -> float:
        if s.is_dark:
            return 18
        else:
            if Hct.is_yellow(s.neutral_palette.hue):
                return 99
            elif s.variant == Variant.VIBRANT:
                return 97
            else:
                return 98

    def _surface_bright_chroma_multiplier_2025(self, s: DynamicScheme) -> float:
        if s.is_dark:
            if s.variant == Variant.NEUTRAL:
                return 2.5
            elif s.variant == Variant.TONAL_SPOT:
                return 1.7
            elif s.variant == Variant.EXPRESSIVE:
                return 2.7 if Hct.is_yellow(s.neutral_palette.hue) else 1.75
            elif s.variant == Variant.VIBRANT:
                return 1.36
        return 1.0

    def surfaceBright(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="surfaceBright",
            palette=lambda s: s.neutral_palette,
            tone=self._surface_bright_tone_2025,
            is_background=True,
            chroma_multiplier=self._surface_bright_chroma_multiplier_2025,
        )
        return extend_spec_version(super().surfaceBright(), "2025", color2025)

    def surfaceContainerLowest(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="surfaceContainerLowest",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 0 if s.is_dark else 100,
            is_background=True,
        )
        return extend_spec_version(super().surfaceContainerLowest(), "2025", color2025)

    def _surface_container_low_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.is_dark:
                return 6
            else:
                if Hct.is_yellow(s.neutral_palette.hue):
                    return 98
                elif s.variant == Variant.VIBRANT:
                    return 95
                else:
                    return 96
        else:
            return 15

    def _surface_container_low_chroma_multiplier_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.variant == Variant.NEUTRAL:
                return 1.3
            elif s.variant == Variant.TONAL_SPOT:
                return 1.25
            elif s.variant == Variant.EXPRESSIVE:
                return 1.3 if Hct.is_yellow(s.neutral_palette.hue) else 1.15
            elif s.variant == Variant.VIBRANT:
                return 1.08
        return 1.0

    def surfaceContainerLow(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="surfaceContainerLow",
            palette=lambda s: s.neutral_palette,
            tone=self._surface_container_low_tone_2025,
            is_background=True,
            chroma_multiplier=self._surface_container_low_chroma_multiplier_2025,
        )
        return extend_spec_version(super().surfaceContainerLow(), "2025", color2025)

    def _surface_container_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.is_dark:
                return 9
            else:
                if Hct.is_yellow(s.neutral_palette.hue):
                    return 96
                elif s.variant == Variant.VIBRANT:
                    return 92
                else:
                    return 94
        else:
            return 20

    def _surface_container_chroma_multiplier_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.variant == Variant.NEUTRAL:
                return 1.6
            elif s.variant == Variant.TONAL_SPOT:
                return 1.4
            elif s.variant == Variant.EXPRESSIVE:
                return 1.6 if Hct.is_yellow(s.neutral_palette.hue) else 1.3
            elif s.variant == Variant.VIBRANT:
                return 1.15
        return 1.0

    def surfaceContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="surfaceContainer",
            palette=lambda s: s.neutral_palette,
            tone=self._surface_container_tone_2025,
            is_background=True,
            chroma_multiplier=self._surface_container_chroma_multiplier_2025,
        )
        return extend_spec_version(super().surfaceContainer(), "2025", color2025)

    def _surface_container_high_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.is_dark:
                return 12
            else:
                if Hct.is_yellow(s.neutral_palette.hue):
                    return 94
                elif s.variant == Variant.VIBRANT:
                    return 90
                else:
                    return 92
        else:
            return 25

    def _surface_container_high_chroma_multiplier_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.variant == Variant.NEUTRAL:
                return 1.9
            elif s.variant == Variant.TONAL_SPOT:
                return 1.5
            elif s.variant == Variant.EXPRESSIVE:
                return 1.95 if Hct.is_yellow(s.neutral_palette.hue) else 1.45
            elif s.variant == Variant.VIBRANT:
                return 1.22
        return 1.0

    def surfaceContainerHigh(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="surfaceContainerHigh",
            palette=lambda s: s.neutral_palette,
            tone=self._surface_container_high_tone_2025,
            is_background=True,
            chroma_multiplier=self._surface_container_high_chroma_multiplier_2025,
        )
        return extend_spec_version(super().surfaceContainerHigh(), "2025", color2025)

    def _surface_container_highest_tone_2025(self, s: DynamicScheme) -> float:
        if s.is_dark:
            return 15
        else:
            if Hct.is_yellow(s.neutral_palette.hue):
                return 92
            elif s.variant == Variant.VIBRANT:
                return 88
            else:
                return 90

    def _surface_container_highest_chroma_multiplier_2025(
        self, s: DynamicScheme
    ) -> float:
        if s.variant == Variant.NEUTRAL:
            return 2.2
        elif s.variant == Variant.TONAL_SPOT:
            return 1.7
        elif s.variant == Variant.EXPRESSIVE:
            return 2.3 if Hct.is_yellow(s.neutral_palette.hue) else 1.6
        elif s.variant == Variant.VIBRANT:
            return 1.29
        else:
            return 1.0

    def surfaceContainerHighest(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="surfaceContainerHighest",
            palette=lambda s: s.neutral_palette,
            tone=self._surface_container_highest_tone_2025,
            is_background=True,
            chroma_multiplier=self._surface_container_highest_chroma_multiplier_2025,
        )
        return extend_spec_version(super().surfaceContainerHighest(), "2025", color2025)

    def _on_surface_tone_2025(self, s: DynamicScheme) -> float:
        if s.variant == Variant.VIBRANT:
            return t_max_c(s.neutral_palette, 0, 100, 1.1)
        else:
            return DynamicColor.get_initial_tone_from_background(
                lambda scheme: self.highestSurface(scheme)
                if scheme.platform == "phone"
                else self.surfaceContainerHigh()
            )(s)

    def _on_surface_chroma_multiplier_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.variant == Variant.NEUTRAL:
                return 2.2
            elif s.variant == Variant.TONAL_SPOT:
                return 1.7
            elif s.variant == Variant.EXPRESSIVE:
                return (
                    3.0
                    if Hct.is_yellow(s.neutral_palette.hue) and s.is_dark
                    else (2.3 if Hct.is_yellow(s.neutral_palette.hue) else 1.6)
                )
        return 1.0

    def _on_surface_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(11) if s.is_dark and s.platform == "phone" else get_curve(9)

    def onSurface(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onSurface",
            palette=lambda s: s.neutral_palette,
            tone=self._on_surface_tone_2025,
            chroma_multiplier=self._on_surface_chroma_multiplier_2025,
            background=lambda s: self.highestSurface(s)
            if s.platform == "phone"
            else self.surfaceContainerHigh(),
            contrast_curve=self._on_surface_contrast_curve_2025,
        )
        return extend_spec_version(super().onSurface(), "2025", color2025)

    def _on_surface_variant_chroma_multiplier_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.variant == Variant.NEUTRAL:
                return 2.2
            elif s.variant == Variant.TONAL_SPOT:
                return 1.7
            elif s.variant == Variant.EXPRESSIVE:
                return (
                    3.0
                    if Hct.is_yellow(s.neutral_palette.hue) and s.is_dark
                    else (2.3 if Hct.is_yellow(s.neutral_palette.hue) else 1.6)
                )
        return 1.0

    def _on_surface_variant_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return (
            get_curve(6)
            if s.platform == "phone" and s.is_dark
            else (get_curve(4.5) if s.platform == "phone" else get_curve(7))
        )

    def onSurfaceVariant(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onSurfaceVariant",
            palette=lambda s: s.neutral_palette,
            chroma_multiplier=self._on_surface_variant_chroma_multiplier_2025,
            background=lambda s: self.highestSurface(s)
            if s.platform == "phone"
            else self.surfaceContainerHigh(),
            contrast_curve=self._on_surface_variant_contrast_curve_2025,
        )
        return extend_spec_version(super().onSurfaceVariant(), "2025", color2025)

    def _outline_chroma_multiplier_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.variant == Variant.NEUTRAL:
                return 2.2
            elif s.variant == Variant.TONAL_SPOT:
                return 1.7
            elif s.variant == Variant.EXPRESSIVE:
                return (
                    3.0
                    if Hct.is_yellow(s.neutral_palette.hue) and s.is_dark
                    else (2.3 if Hct.is_yellow(s.neutral_palette.hue) else 1.6)
                )
        return 1.0

    def _outline_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(3) if s.platform == "phone" else get_curve(4.5)

    def outline(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="outline",
            palette=lambda s: s.neutral_palette,
            chroma_multiplier=self._outline_chroma_multiplier_2025,
            background=lambda s: self.highestSurface(s)
            if s.platform == "phone"
            else self.surfaceContainerHigh(),
            contrast_curve=self._outline_contrast_curve_2025,
        )
        return extend_spec_version(super().outline(), "2025", color2025)

    def _outline_variant_chroma_multiplier_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            if s.variant == Variant.NEUTRAL:
                return 2.2
            elif s.variant == Variant.TONAL_SPOT:
                return 1.7
            elif s.variant == Variant.EXPRESSIVE:
                return (
                    3.0
                    if Hct.is_yellow(s.neutral_palette.hue) and s.is_dark
                    else (2.3 if Hct.is_yellow(s.neutral_palette.hue) else 1.6)
                )
        return 1.0

    def _outline_variant_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(1.5) if s.platform == "phone" else get_curve(3)

    def outlineVariant(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="outlineVariant",
            palette=lambda s: s.neutral_palette,
            chroma_multiplier=self._outline_variant_chroma_multiplier_2025,
            background=lambda s: self.highestSurface(s)
            if s.platform == "phone"
            else self.surfaceContainerHigh(),
            contrast_curve=self._outline_variant_contrast_curve_2025,
        )
        return extend_spec_version(super().outlineVariant(), "2025", color2025)

    def inverseSurface(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="inverseSurface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 98 if s.is_dark else 4,
            is_background=True,
        )
        return extend_spec_version(super().inverseSurface(), "2025", color2025)

    def _inverse_on_surface_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return get_curve(7)

    def inverseOnSurface(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="inverseOnSurface",
            palette=lambda s: s.neutral_palette,
            background=lambda s: self.inverseSurface(),
            contrast_curve=self._inverse_on_surface_contrast_curve_2025,
        )
        return extend_spec_version(super().inverseOnSurface(), "2025", color2025)

    def _primary_tone_2025(self, s: DynamicScheme) -> float:
        if s.variant == Variant.NEUTRAL:
            return (
                80
                if s.platform == "phone" and s.is_dark
                else (40 if s.platform == "phone" else 90)
            )
        elif s.variant == Variant.TONAL_SPOT:
            return (
                80
                if s.platform == "phone" and s.is_dark
                else (
                    t_max_c(s.primary_palette)
                    if s.platform == "phone"
                    else t_max_c(s.primary_palette, 0, 90)
                )
            )
        elif s.variant == Variant.EXPRESSIVE:
            if s.platform == "phone":
                if Hct.is_yellow(s.primary_palette.hue):
                    return t_max_c(s.primary_palette, 0, 25)
                elif Hct.is_cyan(s.primary_palette.hue):
                    return t_max_c(s.primary_palette, 0, 88)
                else:
                    return t_max_c(s.primary_palette, 0, 98)
            else:
                return t_max_c(s.primary_palette)
        elif s.variant == Variant.VIBRANT:
            if s.platform == "phone":
                if Hct.is_cyan(s.primary_palette.hue):
                    return t_max_c(s.primary_palette, 0, 88)
                else:
                    return t_max_c(s.primary_palette, 0, 98)
            else:
                return t_max_c(s.primary_palette)
        return 0.0  # Should not reach here

    def _primary_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(4.5) if s.platform == "phone" else get_curve(7)

    def _primary_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> Optional[ToneDeltaPair]:
        if s.platform == "phone":
            return ToneDeltaPair(
                self.primaryContainer(),
                self.primary(),
                5,
                "relative_lighter",
                True,
                "farther",
            )
        return None

    def primary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="primary",
            palette=lambda s: s.primary_palette,
            tone=self._primary_tone_2025,
            is_background=True,
            background=lambda s: self.highestSurface(s)
            if s.platform == "phone"
            else self.surfaceContainerHigh(),
            contrast_curve=self._primary_contrast_curve_2025,
            tone_delta_pair=self._primary_tone_delta_pair_2025,
        )
        return extend_spec_version(super().primary(), "2025", color2025)

    def primaryDim(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="primaryDim",
            palette=lambda s: s.primary_palette,
            tone=lambda s: (
                85
                if s.variant == Variant.NEUTRAL
                else (
                    t_max_c(s.primary_palette, 0, 90)
                    if s.variant == Variant.TONAL_SPOT
                    else t_max_c(s.primary_palette)
                )
            ),
            is_background=True,
            background=lambda s: self.surfaceContainerHigh(),
            contrast_curve=lambda s: get_curve(4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.primaryDim(), self.primary(), 5, "darker", True, "farther"
            ),
        )

    def _on_primary_background_2025(self, s: DynamicScheme) -> DynamicColor:
        return self.primary() if s.platform == "phone" else self.primaryDim()

    def _on_primary_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(6) if s.platform == "phone" else get_curve(7)

    def onPrimary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onPrimary",
            palette=lambda s: s.primary_palette,
            background=self._on_primary_background_2025,
            contrast_curve=self._on_primary_contrast_curve_2025,
        )
        return extend_spec_version(super().onPrimary(), "2025", color2025)

    def _primary_container_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "watch":
            return 30
        elif s.variant == Variant.NEUTRAL:
            return 30 if s.is_dark else 90
        elif s.variant == Variant.TONAL_SPOT:
            return (
                t_min_c(s.primary_palette, 35, 93)
                if s.is_dark
                else t_max_c(s.primary_palette, 0, 90)
            )
        elif s.variant == Variant.EXPRESSIVE:
            return (
                t_max_c(s.primary_palette, 30, 93)
                if s.is_dark
                else (
                    t_max_c(s.primary_palette, 78, 88)
                    if Hct.is_cyan(s.primary_palette.hue)
                    else t_max_c(s.primary_palette, 78, 90)
                )
            )
        elif s.variant == Variant.VIBRANT:
            return (
                t_min_c(s.primary_palette, 66, 93)
                if s.is_dark
                else (
                    t_max_c(s.primary_palette, 66, 88)
                    if Hct.is_cyan(s.primary_palette.hue)
                    else t_max_c(s.primary_palette, 66, 93)
                )
            )
        return 0.0  # Should not reach here

    def _primary_container_background_2025(
        self, s: DynamicScheme
    ) -> Optional[DynamicColor]:
        return self.highestSurface(s) if s.platform == "phone" else None

    def _primary_container_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> Optional[ToneDeltaPair]:
        if s.platform == "phone":
            return None
        return ToneDeltaPair(
            self.primaryContainer(),
            self.primaryDim(),
            10,
            "darker",
            True,
            "farther",
        )

    def _primary_container_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> Optional[ContrastCurve]:
        if s.platform == "phone" and s.contrast_level > 0:
            return get_curve(1.5)
        return None

    def primaryContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="primaryContainer",
            palette=lambda s: s.primary_palette,
            tone=self._primary_container_tone_2025,
            is_background=True,
            background=self._primary_container_background_2025,
            tone_delta_pair=self._primary_container_tone_delta_pair_2025,
            contrast_curve=self._primary_container_contrast_curve_2025,
        )
        return extend_spec_version(super().primaryContainer(), "2025", color2025)

    def _on_primary_container_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return get_curve(6) if s.platform == "phone" else get_curve(7)

    def onPrimaryContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onPrimaryContainer",
            palette=lambda s: s.primary_palette,
            background=lambda s: self.primaryContainer(),
            contrast_curve=self._on_primary_container_contrast_curve_2025,
        )
        return extend_spec_version(super().onPrimaryContainer(), "2025", color2025)

    def _primary_fixed_tone_2025(self, s: DynamicScheme) -> float:
        # Create a temporary scheme with is_dark=False and contrast_level=0
        # to get the tone from primary_container in a light, normal contrast context.
        temp_s = DynamicScheme(
            source_color_hct=s.source_color_hct,
            variant=s.variant,
            contrast_level=0,
            is_dark=False,
            platform=s.platform,
            spec_version=s.spec_version,
            primary_palette=s.primary_palette,
            secondary_palette=s.secondary_palette,
            tertiary_palette=s.tertiary_palette,
            neutral_palette=s.neutral_palette,
            neutral_variant_palette=s.neutral_variant_palette,
            error_palette=s.error_palette,
        )
        return self.primaryContainer().get_tone(temp_s)

    def _primary_fixed_background_2025(
        self, s: DynamicScheme
    ) -> Optional[DynamicColor]:
        return self.highestSurface(s) if s.platform == "phone" else None

    def _primary_fixed_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> Optional[ContrastCurve]:
        if s.platform == "phone" and s.contrast_level > 0:
            return get_curve(1.5)
        return None

    def primaryFixed(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="primaryFixed",
            palette=lambda s: s.primary_palette,
            tone=self._primary_fixed_tone_2025,
            is_background=True,
            background=self._primary_fixed_background_2025,
            contrast_curve=self._primary_fixed_contrast_curve_2025,
        )
        return extend_spec_version(super().primaryFixed(), "2025", color2025)

    def _primary_fixed_dim_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> ToneDeltaPair:
        return ToneDeltaPair(
            self.primaryFixedDim(), self.primaryFixed(), 5, "darker", True, "exact"
        )

    def primaryFixedDim(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="primaryFixedDim",
            palette=lambda s: s.primary_palette,
            tone=lambda s: self.primaryFixed().get_tone(s),
            is_background=True,
            tone_delta_pair=self._primary_fixed_dim_tone_delta_pair_2025,
        )
        return extend_spec_version(super().primaryFixedDim(), "2025", color2025)

    def _on_primary_fixed_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(7)

    def onPrimaryFixed(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onPrimaryFixed",
            palette=lambda s: s.primary_palette,
            background=lambda s: self.primaryFixedDim(),
            contrast_curve=self._on_primary_fixed_contrast_curve_2025,
        )
        return extend_spec_version(super().onPrimaryFixed(), "2025", color2025)

    def _on_primary_fixed_variant_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return get_curve(4.5)

    def onPrimaryFixedVariant(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onPrimaryFixedVariant",
            palette=lambda s: s.primary_palette,
            background=lambda s: self.primaryFixedDim(),
            contrast_curve=self._on_primary_fixed_variant_contrast_curve_2025,
        )
        return extend_spec_version(super().onPrimaryFixedVariant(), "2025", color2025)

    def _inverse_primary_tone_2025(self, s: DynamicScheme) -> float:
        return t_max_c(s.primary_palette)

    def _inverse_primary_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(6) if s.platform == "phone" else get_curve(7)

    def inversePrimary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="inversePrimary",
            palette=lambda s: s.primary_palette,
            tone=self._inverse_primary_tone_2025,
            background=lambda s: self.inverseSurface(),
            contrast_curve=self._inverse_primary_contrast_curve_2025,
        )
        return extend_spec_version(super().inversePrimary(), "2025", color2025)

    def _secondary_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "watch":
            return (
                90
                if s.variant == Variant.NEUTRAL
                else t_max_c(s.secondary_palette, 0, 90)
            )
        elif s.variant == Variant.NEUTRAL:
            return (
                t_min_c(s.secondary_palette, 0, 98)
                if s.is_dark
                else t_max_c(s.secondary_palette)
            )
        elif s.variant == Variant.VIBRANT:
            return (
                t_max_c(s.secondary_palette, 0, 90)
                if s.is_dark
                else t_max_c(s.secondary_palette, 0, 98)
            )
        else:  # EXPRESSIVE and TONAL_SPOT
            return 80 if s.is_dark else t_max_c(s.secondary_palette)

    def _secondary_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(4.5) if s.platform == "phone" else get_curve(7)

    def _secondary_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> Optional[ToneDeltaPair]:
        if s.platform == "phone":
            return ToneDeltaPair(
                self.secondaryContainer(),
                self.secondary(),
                5,
                "relative_lighter",
                True,
                "farther",
            )
        return None

    def secondary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="secondary",
            palette=lambda s: s.secondary_palette,
            tone=self._secondary_tone_2025,
            is_background=True,
            background=lambda s: self.highestSurface(s)
            if s.platform == "phone"
            else self.surfaceContainerHigh(),
            contrast_curve=self._secondary_contrast_curve_2025,
            tone_delta_pair=self._secondary_tone_delta_pair_2025,
        )
        return extend_spec_version(super().secondary(), "2025", color2025)

    def secondaryDim(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="secondaryDim",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: (
                85
                if s.variant == Variant.NEUTRAL
                else t_max_c(s.secondary_palette, 0, 90)
            ),
            is_background=True,
            background=lambda s: self.surfaceContainerHigh(),
            contrast_curve=lambda s: get_curve(4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.secondaryDim(), self.secondary(), 5, "darker", True, "farther"
            ),
        )

    def _on_secondary_background_2025(self, s: DynamicScheme) -> DynamicColor:
        return self.secondary() if s.platform == "phone" else self.secondaryDim()

    def _on_secondary_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(6) if s.platform == "phone" else get_curve(7)

    def onSecondary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onSecondary",
            palette=lambda s: s.secondary_palette,
            background=self._on_secondary_background_2025,
            contrast_curve=self._on_secondary_contrast_curve_2025,
        )
        return extend_spec_version(super().onSecondary(), "2025", color2025)

    def _secondary_container_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "watch":
            return 30
        elif s.variant == Variant.VIBRANT:
            return (
                t_min_c(s.secondary_palette, 30, 40)
                if s.is_dark
                else t_max_c(s.secondary_palette, 84, 90)
            )
        elif s.variant == Variant.EXPRESSIVE:
            return 15 if s.is_dark else t_max_c(s.secondary_palette, 90, 95)
        else:
            return 25 if s.is_dark else 90

    def _secondary_container_background_2025(
        self, s: DynamicScheme
    ) -> Optional[DynamicColor]:
        return self.highestSurface(s) if s.platform == "phone" else None

    def _secondary_container_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> Optional[ToneDeltaPair]:
        if s.platform == "watch":
            return ToneDeltaPair(
                self.secondaryContainer(),
                self.secondaryDim(),
                10,
                "darker",
                True,
                "farther",
            )
        return None

    def _secondary_container_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> Optional[ContrastCurve]:
        if s.platform == "phone" and s.contrast_level > 0:
            return get_curve(1.5)
        return None

    def secondaryContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="secondaryContainer",
            palette=lambda s: s.secondary_palette,
            tone=self._secondary_container_tone_2025,
            is_background=True,
            background=self._secondary_container_background_2025,
            tone_delta_pair=self._secondary_container_tone_delta_pair_2025,
            contrast_curve=self._secondary_container_contrast_curve_2025,
        )
        return extend_spec_version(super().secondaryContainer(), "2025", color2025)

    def _on_secondary_container_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return get_curve(6) if s.platform == "phone" else get_curve(7)

    def onSecondaryContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onSecondaryContainer",
            palette=lambda s: s.secondary_palette,
            background=lambda s: self.secondaryContainer(),
            contrast_curve=self._on_secondary_container_contrast_curve_2025,
        )
        return extend_spec_version(super().onSecondaryContainer(), "2025", color2025)

    def _secondary_fixed_tone_2025(self, s: DynamicScheme) -> float:
        temp_s = DynamicScheme(
            source_color_hct=s.source_color_hct,
            variant=s.variant,
            contrast_level=0,
            is_dark=False,
            platform=s.platform,
            spec_version=s.spec_version,
            primary_palette=s.primary_palette,
            secondary_palette=s.secondary_palette,
            tertiary_palette=s.tertiary_palette,
            neutral_palette=s.neutral_palette,
            neutral_variant_palette=s.neutral_variant_palette,
            error_palette=s.error_palette,
        )
        return self.secondaryContainer().get_tone(temp_s)

    def _secondary_fixed_background_2025(
        self, s: DynamicScheme
    ) -> Optional[DynamicColor]:
        return self.highestSurface(s) if s.platform == "phone" else None

    def _secondary_fixed_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> Optional[ContrastCurve]:
        if s.platform == "phone" and s.contrast_level > 0:
            return get_curve(1.5)
        return None

    def secondaryFixed(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="secondaryFixed",
            palette=lambda s: s.secondary_palette,
            tone=self._secondary_fixed_tone_2025,
            is_background=True,
            background=self._secondary_fixed_background_2025,
            contrast_curve=self._secondary_fixed_contrast_curve_2025,
        )
        return extend_spec_version(super().secondaryFixed(), "2025", color2025)

    def _secondary_fixed_dim_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> ToneDeltaPair:
        return ToneDeltaPair(
            self.secondaryFixedDim(),
            self.secondaryFixed(),
            5,
            "darker",
            True,
            "exact",
        )

    def secondaryFixedDim(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="secondaryFixedDim",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: self.secondaryFixed().get_tone(s),
            is_background=True,
            tone_delta_pair=self._secondary_fixed_dim_tone_delta_pair_2025,
        )
        return extend_spec_version(super().secondaryFixedDim(), "2025", color2025)

    def _on_secondary_fixed_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return get_curve(7)

    def onSecondaryFixed(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onSecondaryFixed",
            palette=lambda s: s.secondary_palette,
            background=lambda s: self.secondaryFixedDim(),
            contrast_curve=self._on_secondary_fixed_contrast_curve_2025,
        )
        return extend_spec_version(super().onSecondaryFixed(), "2025", color2025)

    def _on_secondary_fixed_variant_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return get_curve(4.5)

    def onSecondaryFixedVariant(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onSecondaryFixedVariant",
            palette=lambda s: s.secondary_palette,
            background=lambda s: self.secondaryFixedDim(),
            contrast_curve=self._on_secondary_fixed_variant_contrast_curve_2025,
        )
        return extend_spec_version(super().onSecondaryFixedVariant(), "2025", color2025)

    def _tertiary_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "watch":
            return (
                t_max_c(s.tertiary_palette, 0, 90)
                if s.variant == Variant.TONAL_SPOT
                else t_max_c(s.tertiary_palette)
            )
        elif s.variant == Variant.EXPRESSIVE or s.variant == Variant.VIBRANT:
            if Hct.is_cyan(s.tertiary_palette.hue):
                return t_max_c(s.tertiary_palette, 0, 88)
            elif s.is_dark:
                return t_max_c(s.tertiary_palette, 0, 98)
            else:
                return t_max_c(s.tertiary_palette, 0, 100)
        else:  # NEUTRAL and TONAL_SPOT
            return (
                t_max_c(s.tertiary_palette, 0, 98)
                if s.is_dark
                else t_max_c(s.tertiary_palette)
            )

    def _tertiary_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(4.5) if s.platform == "phone" else get_curve(7)

    def _tertiary_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> Optional[ToneDeltaPair]:
        if s.platform == "phone":
            return ToneDeltaPair(
                self.tertiaryContainer(),
                self.tertiary(),
                5,
                "relative_lighter",
                True,
                "farther",
            )
        return None

    def tertiary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="tertiary",
            palette=lambda s: s.tertiary_palette,
            tone=self._tertiary_tone_2025,
            is_background=True,
            background=lambda s: self.highestSurface(s)
            if s.platform == "phone"
            else self.surfaceContainerHigh(),
            contrast_curve=self._tertiary_contrast_curve_2025,
            tone_delta_pair=self._tertiary_tone_delta_pair_2025,
        )
        return extend_spec_version(super().tertiary(), "2025", color2025)

    def tertiaryDim(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="tertiaryDim",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: (
                t_max_c(s.tertiary_palette, 0, 90)
                if s.variant == Variant.TONAL_SPOT
                else t_max_c(s.tertiary_palette)
            ),
            is_background=True,
            background=lambda s: self.surfaceContainerHigh(),
            contrast_curve=lambda s: get_curve(4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.tertiaryDim(), self.tertiary(), 5, "darker", True, "farther"
            ),
        )

    def _on_tertiary_background_2025(self, s: DynamicScheme) -> DynamicColor:
        return self.tertiary() if s.platform == "phone" else self.tertiaryDim()

    def _on_tertiary_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(6) if s.platform == "phone" else get_curve(7)

    def onTertiary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onTertiary",
            palette=lambda s: s.tertiary_palette,
            background=self._on_tertiary_background_2025,
            contrast_curve=self._on_tertiary_contrast_curve_2025,
        )
        return extend_spec_version(super().onTertiary(), "2025", color2025)

    def _tertiary_container_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "watch":
            return (
                t_max_c(s.tertiary_palette, 0, 90)
                if s.variant == Variant.TONAL_SPOT
                else t_max_c(s.tertiary_palette)
            )
        elif s.variant == Variant.NEUTRAL:
            return (
                t_max_c(s.tertiary_palette, 0, 93)
                if s.is_dark
                else t_max_c(s.tertiary_palette, 0, 96)
            )
        elif s.variant == Variant.TONAL_SPOT:
            return (
                t_max_c(s.tertiary_palette, 0, 93)
                if s.is_dark
                else t_max_c(s.tertiary_palette, 0, 100)
            )
        elif s.variant == Variant.EXPRESSIVE:
            if Hct.is_cyan(s.tertiary_palette.hue):
                return t_max_c(s.tertiary_palette, 75, 88)
            elif s.is_dark:
                return t_max_c(s.tertiary_palette, 75, 93)
            else:
                return t_max_c(s.tertiary_palette, 75, 100)
        elif s.variant == Variant.VIBRANT:
            return (
                t_max_c(s.tertiary_palette, 0, 93)
                if s.is_dark
                else t_max_c(s.tertiary_palette, 72, 100)
            )
        return 0.0  # Should not reach here

    def _tertiary_container_background_2025(
        self, s: DynamicScheme
    ) -> Optional[DynamicColor]:
        return self.highestSurface(s) if s.platform == "phone" else None

    def _tertiary_container_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> Optional[ToneDeltaPair]:
        if s.platform == "watch":
            return ToneDeltaPair(
                self.tertiaryContainer(),
                self.tertiaryDim(),
                10,
                "darker",
                True,
                "farther",
            )
        return None

    def _tertiary_container_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> Optional[ContrastCurve]:
        if s.platform == "phone" and s.contrast_level > 0:
            return get_curve(1.5)
        return None

    def tertiaryContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="tertiaryContainer",
            palette=lambda s: s.tertiary_palette,
            tone=self._tertiary_container_tone_2025,
            is_background=True,
            background=self._tertiary_container_background_2025,
            tone_delta_pair=self._tertiary_container_tone_delta_pair_2025,
            contrast_curve=self._tertiary_container_contrast_curve_2025,
        )
        return extend_spec_version(super().tertiaryContainer(), "2025", color2025)

    def _on_tertiary_container_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return get_curve(6) if s.platform == "phone" else get_curve(7)

    def onTertiaryContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onTertiaryContainer",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: self.tertiaryContainer(),
            contrast_curve=self._on_tertiary_container_contrast_curve_2025,
        )
        return extend_spec_version(super().onTertiaryContainer(), "2025", color2025)

    def _tertiary_fixed_tone_2025(self, s: DynamicScheme) -> float:
        temp_s = DynamicScheme(
            source_color_hct=s.source_color_hct,
            variant=s.variant,
            contrast_level=0,
            is_dark=False,
            platform=s.platform,
            spec_version=s.spec_version,
            primary_palette=s.primary_palette,
            secondary_palette=s.secondary_palette,
            tertiary_palette=s.tertiary_palette,
            neutral_palette=s.neutral_palette,
            neutral_variant_palette=s.neutral_variant_palette,
            error_palette=s.error_palette,
        )
        return self.tertiaryContainer().get_tone(temp_s)

    def _tertiary_fixed_background_2025(
        self, s: DynamicScheme
    ) -> Optional[DynamicColor]:
        return self.highestSurface(s) if s.platform == "phone" else None

    def _tertiary_fixed_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> Optional[ContrastCurve]:
        if s.platform == "phone" and s.contrast_level > 0:
            return get_curve(1.5)
        return None

    def tertiaryFixed(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="tertiaryFixed",
            palette=lambda s: s.tertiary_palette,
            tone=self._tertiary_fixed_tone_2025,
            is_background=True,
            background=self._tertiary_fixed_background_2025,
            contrast_curve=self._tertiary_fixed_contrast_curve_2025,
        )
        return extend_spec_version(super().tertiaryFixed(), "2025", color2025)

    def _tertiary_fixed_dim_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> ToneDeltaPair:
        return ToneDeltaPair(
            self.tertiaryFixedDim(), self.tertiaryFixed(), 5, "darker", True, "exact"
        )

    def tertiaryFixedDim(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="tertiaryFixedDim",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: self.tertiaryFixed().get_tone(s),
            is_background=True,
            tone_delta_pair=self._tertiary_fixed_dim_tone_delta_pair_2025,
        )
        return extend_spec_version(super().tertiaryFixedDim(), "2025", color2025)

    def _on_tertiary_fixed_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(7)

    def onTertiaryFixed(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onTertiaryFixed",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: self.tertiaryFixedDim(),
            contrast_curve=self._on_tertiary_fixed_contrast_curve_2025,
        )
        return extend_spec_version(super().onTertiaryFixed(), "2025", color2025)

    def _on_tertiary_fixed_variant_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return get_curve(4.5)

    def onTertiaryFixedVariant(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onTertiaryFixedVariant",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: self.tertiaryFixedDim(),
            contrast_curve=self._on_tertiary_fixed_variant_contrast_curve_2025,
        )
        return extend_spec_version(super().onTertiaryFixedVariant(), "2025", color2025)

    def _error_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "phone":
            return (
                t_min_c(s.error_palette, 0, 98)
                if s.is_dark
                else t_max_c(s.error_palette)
            )
        else:
            return t_min_c(s.error_palette)

    def _error_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(4.5) if s.platform == "phone" else get_curve(7)

    def _error_tone_delta_pair_2025(self, s: DynamicScheme) -> Optional[ToneDeltaPair]:
        if s.platform == "phone":
            return ToneDeltaPair(
                self.errorContainer(),
                self.error(),
                5,
                "relative_lighter",
                True,
                "farther",
            )
        return None

    def error(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="error",
            palette=lambda s: s.error_palette,
            tone=self._error_tone_2025,
            is_background=True,
            background=lambda s: self.highestSurface(s)
            if s.platform == "phone"
            else self.surfaceContainerHigh(),
            contrast_curve=self._error_contrast_curve_2025,
            tone_delta_pair=self._error_tone_delta_pair_2025,
        )
        return extend_spec_version(super().error(), "2025", color2025)

    def errorDim(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="errorDim",
            palette=lambda s: s.error_palette,
            tone=lambda s: t_min_c(s.error_palette),
            is_background=True,
            background=lambda s: self.surfaceContainerHigh(),
            contrast_curve=lambda s: get_curve(4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.errorDim(), self.error(), 5, "darker", True, "farther"
            ),
        )

    def _on_error_background_2025(self, s: DynamicScheme) -> DynamicColor:
        return self.error() if s.platform == "phone" else self.errorDim()

    def _on_error_contrast_curve_2025(self, s: DynamicScheme) -> ContrastCurve:
        return get_curve(6) if s.platform == "phone" else get_curve(7)

    def onError(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onError",
            palette=lambda s: s.error_palette,
            background=self._on_error_background_2025,
            contrast_curve=self._on_error_contrast_curve_2025,
        )
        return extend_spec_version(super().onError(), "2025", color2025)

    def _error_container_tone_2025(self, s: DynamicScheme) -> float:
        if s.platform == "watch":
            return 30
        else:
            return (
                t_min_c(s.error_palette, 30, 93)
                if s.is_dark
                else t_max_c(s.error_palette, 0, 90)
            )

    def _error_container_background_2025(
        self, s: DynamicScheme
    ) -> Optional[DynamicColor]:
        return self.highestSurface(s) if s.platform == "phone" else None

    def _error_container_tone_delta_pair_2025(
        self, s: DynamicScheme
    ) -> Optional[ToneDeltaPair]:
        if s.platform == "watch":
            return ToneDeltaPair(
                self.errorContainer(),
                self.errorDim(),
                10,
                "darker",
                True,
                "farther",
            )
        return None

    def _error_container_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> Optional[ContrastCurve]:
        if s.platform == "phone" and s.contrast_level > 0:
            return get_curve(1.5)
        return None

    def errorContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="errorContainer",
            palette=lambda s: s.error_palette,
            tone=self._error_container_tone_2025,
            is_background=True,
            background=self._error_container_background_2025,
            tone_delta_pair=self._error_container_tone_delta_pair_2025,
            contrast_curve=self._error_container_contrast_curve_2025,
        )
        return extend_spec_version(super().errorContainer(), "2025", color2025)

    def _on_error_container_contrast_curve_2025(
        self, s: DynamicScheme
    ) -> ContrastCurve:
        return get_curve(4.5) if s.platform == "phone" else get_curve(7)

    def onErrorContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onErrorContainer",
            palette=lambda s: s.error_palette,
            background=lambda s: self.errorContainer(),
            contrast_curve=self._on_error_container_contrast_curve_2025,
        )
        return extend_spec_version(super().onErrorContainer(), "2025", color2025)

    def surfaceVariant(self) -> DynamicColor:
        color2025 = self.surfaceContainerHighest().clone()
        color2025.name = "surfaceVariant"
        return extend_spec_version(super().surfaceVariant(), "2025", color2025)

    def surfaceTint(self) -> DynamicColor:
        color2025 = self.primary().clone()
        color2025.name = "surfaceTint"
        return extend_spec_version(super().surfaceTint(), "2025", color2025)

    def background(self) -> DynamicColor:
        color2025 = self.surface().clone()
        color2025.name = "background"
        return extend_spec_version(super().background(), "2025", color2025)

    def onBackground(self) -> DynamicColor:
        color2025 = self.onSurface().clone()
        color2025.name = "onBackground"
        color2025.tone = (
            lambda s: 100.0 if s.platform == "watch" else self.onSurface().get_tone(s)
        )
        return extend_spec_version(super().onBackground(), "2025", color2025)
