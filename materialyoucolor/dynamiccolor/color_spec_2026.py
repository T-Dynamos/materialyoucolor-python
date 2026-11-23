from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Optional

from materialyoucolor.dynamiccolor.color_spec_2025 import (
    ColorSpecDelegateImpl2025,
    get_curve,
    t_max_c,
    t_min_c,
)
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve
from materialyoucolor.dynamiccolor.dynamic_color import (
    DynamicColor,
    extend_spec_version,
)
from materialyoucolor.dynamiccolor.tone_delta_pair import ToneDeltaPair
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct
from materialyoucolor.utils.math_utils import clamp_double

if TYPE_CHECKING:
    from materialyoucolor.dynamiccolor.dynamic_scheme import DynamicScheme


def _temp_light_standard(s: "DynamicScheme") -> "DynamicScheme":
    temp_s = copy.copy(s)
    temp_s.is_dark = False
    temp_s.contrast_level = 0.0
    return temp_s


class ColorSpecDelegateImpl2026(ColorSpecDelegateImpl2025):
    """
    A delegate for the dynamic color spec of a DynamicScheme in the 2026 spec.
    """

    def surface(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="surface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (4 if s.is_dark else 98) if s.variant == Variant.CMF else 0,
            is_background=True,
        )
        return extend_spec_version(super().surface(), "2026", color2026)

    def surfaceDim(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="surfaceDim",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (4 if s.is_dark else 87) if s.variant == Variant.CMF else 0,
            chroma_multiplier=lambda s: (
                (1.0 if s.is_dark else 1.7) if s.variant == Variant.CMF else 0.0
            ),
            is_background=True,
        )
        return extend_spec_version(super().surfaceDim(), "2026", color2026)

    def surfaceBright(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="surfaceBright",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (18 if s.is_dark else 98) if s.variant == Variant.CMF else 0,
            chroma_multiplier=lambda s: (
                (1.7 if s.is_dark else 1.0) if s.variant == Variant.CMF else 0.0
            ),
            is_background=True,
        )
        return extend_spec_version(super().surfaceBright(), "2026", color2026)

    def surfaceContainerLowest(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="surfaceContainerLowest",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (0 if s.is_dark else 100) if s.variant == Variant.CMF else 0,
            is_background=True,
        )
        return extend_spec_version(super().surfaceContainerLowest(), "2026", color2026)

    def surfaceContainerLow(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="surfaceContainerLow",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (6 if s.is_dark else 96) if s.variant == Variant.CMF else 0,
            chroma_multiplier=lambda s: 1.25 if s.variant == Variant.CMF else 0.0,
            is_background=True,
        )
        return extend_spec_version(super().surfaceContainerLow(), "2026", color2026)

    def surfaceContainer(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="surfaceContainer",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (9 if s.is_dark else 94) if s.variant == Variant.CMF else 0,
            chroma_multiplier=lambda s: 1.4 if s.variant == Variant.CMF else 0.0,
            is_background=True,
        )
        return extend_spec_version(super().surfaceContainer(), "2026", color2026)

    def surfaceContainerHigh(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="surfaceContainerHigh",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (12 if s.is_dark else 92) if s.variant == Variant.CMF else 0,
            chroma_multiplier=lambda s: 1.5 if s.variant == Variant.CMF else 0.0,
            is_background=True,
        )
        return extend_spec_version(super().surfaceContainerHigh(), "2026", color2026)

    def surfaceContainerHighest(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="surfaceContainerHighest",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (15 if s.is_dark else 90) if s.variant == Variant.CMF else 0,
            chroma_multiplier=lambda s: 1.7 if s.variant == Variant.CMF else 0.0,
            is_background=True,
        )
        return extend_spec_version(super().surfaceContainerHighest(), "2026", color2026)

    def onSurface(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onSurface",
            palette=lambda s: s.neutral_palette,
            chroma_multiplier=lambda s: 1.7 if s.variant == Variant.CMF else 0.0,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: get_curve(11) if s.is_dark else get_curve(9),
        )
        return extend_spec_version(super().onSurface(), "2026", color2026)

    def onSurfaceVariant(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onSurfaceVariant",
            palette=lambda s: s.neutral_palette,
            chroma_multiplier=lambda s: 1.7 if s.variant == Variant.CMF else 0.0,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: get_curve(6) if s.is_dark else get_curve(4.5),
        )
        return extend_spec_version(super().onSurfaceVariant(), "2026", color2026)

    def outline(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="outline",
            palette=lambda s: s.neutral_palette,
            chroma_multiplier=lambda s: 1.7 if s.variant == Variant.CMF else 0.0,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: get_curve(3),
        )
        return extend_spec_version(super().outline(), "2026", color2026)

    def outlineVariant(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="outlineVariant",
            palette=lambda s: s.neutral_palette,
            chroma_multiplier=lambda s: 1.7 if s.variant == Variant.CMF else 0.0,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: get_curve(1.5),
        )
        return extend_spec_version(super().outlineVariant(), "2026", color2026)

    def inverseSurface(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="inverseSurface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 98 if s.is_dark else 4,
            chroma_multiplier=lambda s: 1.7 if s.variant == Variant.CMF else 0.0,
            is_background=True,
        )
        return extend_spec_version(super().inverseSurface(), "2026", color2026)

    def inverseOnSurface(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="inverseOnSurface",
            palette=lambda s: s.neutral_palette,
            background=lambda s: self.inverseSurface(),
            contrast_curve=lambda s: get_curve(7),
        )
        return extend_spec_version(super().inverseOnSurface(), "2026", color2026)

    def primary(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="primary",
            palette=lambda s: s.primary_palette,
            tone=lambda s: (
                (80 if s.is_dark else 40)
                if s.source_color_hct.chroma <= 12
                else s.source_color_hct.tone
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: get_curve(4.5),
            tone_delta_pair=lambda s: (
                ToneDeltaPair(
                    self.primaryContainer(),
                    self.primary(),
                    5,
                    "relative_lighter",
                    True,
                    "farther",
                )
                if s.platform == "phone"
                else None
            ),
        )
        return extend_spec_version(super().primary(), "2026", color2026)

    def onPrimary(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onPrimary",
            palette=lambda s: s.primary_palette,
            background=lambda s: self.primary(),
            contrast_curve=lambda s: get_curve(6),
        )
        return extend_spec_version(super().onPrimary(), "2026", color2026)

    def primaryContainer(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if not s.is_dark and s.source_color_hct.chroma <= 12:
                return 90
            return (
                clamp_double(61, 90, s.source_color_hct.tone)
                if s.source_color_hct.tone > 55
                else clamp_double(30, 49, s.source_color_hct.tone)
            )

        color2026 = DynamicColor.from_palette(
            name="primaryContainer",
            palette=lambda s: s.primary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().primaryContainer(), "2026", color2026)

    def onPrimaryContainer(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onPrimaryContainer",
            palette=lambda s: s.primary_palette,
            background=lambda s: self.primaryContainer(),
            contrast_curve=lambda s: get_curve(6),
        )
        return extend_spec_version(super().onPrimaryContainer(), "2026", color2026)

    def primaryFixed(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="primaryFixed",
            palette=lambda s: s.primary_palette,
            tone=lambda s: self.primaryContainer().get_tone(_temp_light_standard(s)),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().primaryFixed(), "2026", color2026)

    def primaryFixedDim(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="primaryFixedDim",
            palette=lambda s: s.primary_palette,
            tone=lambda s: self.primaryFixed().get_tone(s),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.primaryFixedDim(), self.primaryFixed(), 5, "darker", True, "exact"
            ),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().primaryFixedDim(), "2026", color2026)

    def onPrimaryFixed(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onPrimaryFixed",
            palette=lambda s: s.primary_palette,
            background=lambda s: (
                self.primaryFixedDim()
                if self.primaryFixed().get_tone(s) > 57
                else self.primaryFixed()
            ),
            contrast_curve=lambda s: get_curve(7),
        )
        return extend_spec_version(super().onPrimaryFixed(), "2026", color2026)

    def onPrimaryFixedVariant(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onPrimaryFixedVariant",
            palette=lambda s: s.primary_palette,
            background=lambda s: (
                self.primaryFixedDim()
                if self.primaryFixed().get_tone(s) > 57
                else self.primaryFixed()
            ),
            contrast_curve=lambda s: get_curve(4.5),
        )
        return extend_spec_version(super().onPrimaryFixedVariant(), "2026", color2026)

    def inversePrimary(self) -> DynamicColor:
        return super().inversePrimary()

    def secondary(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="secondary",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: (
                t_min_c(s.secondary_palette)
                if s.is_dark
                else t_max_c(s.secondary_palette)
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: get_curve(4.5),
            tone_delta_pair=lambda s: (
                ToneDeltaPair(
                    self.secondaryContainer(),
                    self.secondary(),
                    5,
                    "relative_lighter",
                    True,
                    "farther",
                )
                if s.platform == "phone"
                else None
            ),
        )
        return extend_spec_version(super().secondary(), "2026", color2026)

    def onSecondary(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onSecondary",
            palette=lambda s: s.secondary_palette,
            background=lambda s: self.secondary(),
            contrast_curve=lambda s: get_curve(6),
        )
        return extend_spec_version(super().onSecondary(), "2026", color2026)

    def secondaryContainer(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="secondaryContainer",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: (
                t_min_c(s.secondary_palette, 20, 49)
                if s.is_dark
                else t_max_c(s.secondary_palette, 61, 90)
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().secondaryContainer(), "2026", color2026)

    def onSecondaryContainer(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onSecondaryContainer",
            palette=lambda s: s.secondary_palette,
            background=lambda s: self.secondaryContainer(),
            contrast_curve=lambda s: get_curve(6),
        )
        return extend_spec_version(super().onSecondaryContainer(), "2026", color2026)

    def secondaryFixed(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="secondaryFixed",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: self.secondaryContainer().get_tone(_temp_light_standard(s)),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().secondaryFixed(), "2026", color2026)

    def secondaryFixedDim(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="secondaryFixedDim",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: self.secondaryFixed().get_tone(s),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.secondaryFixedDim(),
                self.secondaryFixed(),
                5,
                "darker",
                True,
                "exact",
            ),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().secondaryFixedDim(), "2026", color2026)

    def onSecondaryFixed(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onSecondaryFixed",
            palette=lambda s: s.secondary_palette,
            background=lambda s: (
                self.secondaryFixedDim()
                if self.secondaryFixed().get_tone(s) > 57
                else self.secondaryFixed()
            ),
            contrast_curve=lambda s: get_curve(7),
        )
        return extend_spec_version(super().onSecondaryFixed(), "2026", color2026)

    def onSecondaryFixedVariant(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onSecondaryFixedVariant",
            palette=lambda s: s.secondary_palette,
            background=lambda s: (
                self.secondaryFixedDim()
                if self.secondaryFixed().get_tone(s) > 57
                else self.secondaryFixed()
            ),
            contrast_curve=lambda s: get_curve(4.5),
        )
        return extend_spec_version(
            super().onSecondaryFixedVariant(), "2026", color2026
        )

    def tertiary(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="tertiary",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: (
                s.source_color_hcts[1].tone
                if len(s.source_color_hcts) > 1
                else s.source_color_hct.tone
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: get_curve(4.5),
            tone_delta_pair=lambda s: (
                ToneDeltaPair(
                    self.tertiaryContainer(),
                    self.tertiary(),
                    5,
                    "relative_lighter",
                    True,
                    "farther",
                )
                if s.platform == "phone"
                else None
            ),
        )
        return extend_spec_version(super().tertiary(), "2026", color2026)

    def onTertiary(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onTertiary",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: self.tertiary(),
            contrast_curve=lambda s: get_curve(6),
        )
        return extend_spec_version(super().onTertiary(), "2026", color2026)

    def tertiaryContainer(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            sec = (
                s.source_color_hcts[1]
                if len(s.source_color_hcts) > 1
                else s.source_color_hct
            )
            return (
                clamp_double(61, 90, sec.tone)
                if sec.tone > 55
                else clamp_double(20, 49, sec.tone)
            )

        color2026 = DynamicColor.from_palette(
            name="tertiaryContainer",
            palette=lambda s: s.tertiary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().tertiaryContainer(), "2026", color2026)

    def onTertiaryContainer(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onTertiaryContainer",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: self.tertiaryContainer(),
            contrast_curve=lambda s: get_curve(6),
        )
        return extend_spec_version(super().onTertiaryContainer(), "2026", color2026)

    def tertiaryFixed(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="tertiaryFixed",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: self.tertiaryContainer().get_tone(_temp_light_standard(s)),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().tertiaryFixed(), "2026", color2026)

    def tertiaryFixedDim(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="tertiaryFixedDim",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: self.tertiaryFixed().get_tone(s),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.tertiaryFixedDim(),
                self.tertiaryFixed(),
                5,
                "darker",
                True,
                "exact",
            ),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().tertiaryFixedDim(), "2026", color2026)

    def onTertiaryFixed(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onTertiaryFixed",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: (
                self.tertiaryFixedDim()
                if self.tertiaryFixed().get_tone(s) > 57
                else self.tertiaryFixed()
            ),
            contrast_curve=lambda s: get_curve(7),
        )
        return extend_spec_version(super().onTertiaryFixed(), "2026", color2026)

    def onTertiaryFixedVariant(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onTertiaryFixedVariant",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: (
                self.tertiaryFixedDim()
                if self.tertiaryFixed().get_tone(s) > 57
                else self.tertiaryFixed()
            ),
            contrast_curve=lambda s: get_curve(4.5),
        )
        return extend_spec_version(
            super().onTertiaryFixedVariant(), "2026", color2026
        )

    def error(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="error",
            palette=lambda s: s.error_palette,
            tone=lambda s: t_max_c(s.error_palette),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: get_curve(4.5),
            tone_delta_pair=lambda s: (
                ToneDeltaPair(
                    self.errorContainer(),
                    self.error(),
                    5,
                    "relative_lighter",
                    True,
                    "farther",
                )
                if s.platform == "phone"
                else None
            ),
        )
        return extend_spec_version(super().error(), "2026", color2026)

    def onError(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onError",
            palette=lambda s: s.error_palette,
            background=lambda s: self.error(),
            contrast_curve=lambda s: get_curve(6),
        )
        return extend_spec_version(super().onError(), "2026", color2026)

    def errorContainer(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="errorContainer",
            palette=lambda s: s.error_palette,
            tone=lambda s: (
                t_min_c(s.error_palette) if s.is_dark else t_max_c(s.error_palette)
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: (
                get_curve(1.5) if s.contrast_level > 0 else None
            ),
        )
        return extend_spec_version(super().errorContainer(), "2026", color2026)

    def onErrorContainer(self) -> DynamicColor:
        color2026 = DynamicColor.from_palette(
            name="onErrorContainer",
            palette=lambda s: s.error_palette,
            background=lambda s: self.errorContainer(),
            contrast_curve=lambda s: get_curve(6),
        )
        return extend_spec_version(super().onErrorContainer(), "2026", color2026)

    #################################################################
    # Remapped Colors                                               #
    #################################################################

    def primaryDim(self) -> DynamicColor:
        color2026 = self.primary().clone()
        color2026.name = "primaryDim"
        return extend_spec_version(super().primaryDim(), "2026", color2026)

    def secondaryDim(self) -> DynamicColor:
        color2026 = self.secondary().clone()
        color2026.name = "secondaryDim"
        return extend_spec_version(super().secondaryDim(), "2026", color2026)

    def tertiaryDim(self) -> DynamicColor:
        color2026 = self.tertiary().clone()
        color2026.name = "tertiaryDim"
        return extend_spec_version(super().tertiaryDim(), "2026", color2026)

    def errorDim(self) -> DynamicColor:
        color2026 = self.error().clone()
        color2026.name = "errorDim"
        return extend_spec_version(super().errorDim(), "2026", color2026)
