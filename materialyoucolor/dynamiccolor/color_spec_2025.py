from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from materialyoucolor.dynamiccolor.color_spec_2021 import (
    ColorSpecDelegateImpl2021,
)
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve
from materialyoucolor.dynamiccolor.dynamic_color import (
    DynamicColor,
    extend_spec_version,
)
from materialyoucolor.dynamiccolor.tone_delta_pair import ToneDeltaPair
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.utils.math_utils import clamp_double

if TYPE_CHECKING:
    from materialyoucolor.dynamiccolor.dynamic_scheme import DynamicScheme


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


def is_close_to_chroma(hct: Hct, chroma: float) -> bool:
    return abs(hct.chroma - chroma) < 0.4


def find_desired_chroma_by_tone(
    hue: float, chroma: float, starting_tone: float, ending_tone: float
) -> float:
    if ending_tone == starting_tone:
        return starting_tone

    answer = starting_tone
    potential_answer = answer
    increment = -1.0 if ending_tone < starting_tone else 1.0

    closest_to_chroma = Hct.from_hct(hue, chroma, starting_tone)
    while (
        closest_to_chroma.chroma < chroma
        and not is_close_to_chroma(closest_to_chroma, chroma)
    ):
        potential_answer += increment
        if potential_answer < ending_tone and ending_tone < starting_tone:
            return answer
        elif potential_answer > ending_tone and ending_tone > starting_tone:
            return answer
        potential_solution = Hct.from_hct(hue, chroma, potential_answer)
        if is_close_to_chroma(potential_solution, chroma):
            return potential_answer

        potential_delta = abs(potential_solution.chroma - chroma)
        current_delta = abs(closest_to_chroma.chroma - chroma)
        if potential_delta < current_delta:
            closest_to_chroma = potential_solution
            answer = potential_answer

    return answer


def main_tone(tonal_palette: TonalPalette, max_tone: float) -> float:
    ending_tone = DynamicColor.foreground_tone(25.0, 7.0)
    return find_desired_chroma_by_tone(
        tonal_palette.hue, tonal_palette.chroma, max_tone, ending_tone
    )


def dim_tone(tonal_palette: TonalPalette, max_tone: float) -> float:
    initial_tone = min(main_tone(tonal_palette, max_tone) - 5.0, max_tone)
    ending_tone = DynamicColor.foreground_tone(25.0, 4.5)
    return find_desired_chroma_by_tone(
        tonal_palette.hue, tonal_palette.chroma, initial_tone, ending_tone
    )


def container_tone(tonal_palette: TonalPalette, max_tone: float) -> float:
    initial_tone = min(dim_tone(tonal_palette, max_tone) - 5.0, max_tone)
    ending_tone = DynamicColor.foreground_tone(0.0, 7.0)
    return find_desired_chroma_by_tone(
        tonal_palette.hue, tonal_palette.chroma, initial_tone, ending_tone
    )


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


def _temp_light_standard(s: "DynamicScheme") -> "DynamicScheme":
    temp_s = copy.copy(s)
    temp_s.is_dark = False
    temp_s.contrast_level = 0.0
    return temp_s


class ColorSpecDelegateImpl2025(ColorSpecDelegateImpl2021):
    def surface(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            super(ColorSpecDelegateImpl2025, self).surface().tone(s)
            if s.platform == "phone":
                if s.is_dark:
                    return 4.0
                else:
                    if Hct.is_yellow(s.neutral_palette.hue):
                        return 99.0
                    elif s.variant == Variant.VIBRANT:
                        return 97.0
                    else:
                        return 98.0
            else:
                return 0.0

        color2025 = DynamicColor.from_palette(
            name="surface",
            palette=lambda s: s.neutral_palette,
            tone=_tone,
            is_background=True,
        )
        return extend_spec_version(super().surface(), "2025", color2025)

    def surfaceDim(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.is_dark or s.platform == "watch":
                return 4.0
            else:
                if Hct.is_yellow(s.neutral_palette.hue):
                    return 90.0
                elif s.variant == Variant.VIBRANT:
                    return 85.0
                else:
                    return 87.0

        def _chroma_multiplier(s: "DynamicScheme") -> float:
            if not s.is_dark and s.platform == "phone":
                if s.variant == Variant.NEUTRAL:
                    return 2.5
                elif s.variant == Variant.TONAL_SPOT:
                    return 1.7
                elif s.variant == Variant.EXPRESSIVE:
                    return 2.7 if Hct.is_yellow(s.neutral_palette.hue) else 1.75
                elif s.variant == Variant.VIBRANT:
                    return 1.36
            return 1.0

        color2025 = DynamicColor.from_palette(
            name="surfaceDim",
            palette=lambda s: s.neutral_palette,
            tone=_tone,
            is_background=True,
            chroma_multiplier=_chroma_multiplier,
        )
        return extend_spec_version(super().surfaceDim(), "2025", color2025)

    def surfaceBright(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.is_dark or s.platform == "watch":
                return 18.0
            else:
                if Hct.is_yellow(s.neutral_palette.hue):
                    return 99.0
                elif s.variant == Variant.VIBRANT:
                    return 97.0
                else:
                    return 98.0

        def _chroma_multiplier(s: "DynamicScheme") -> float:
            if s.is_dark or s.platform == "watch":
                if s.variant == Variant.NEUTRAL:
                    return 2.5
                elif s.variant == Variant.TONAL_SPOT:
                    return 1.7
                elif s.variant == Variant.EXPRESSIVE:
                    return 2.7 if Hct.is_yellow(s.neutral_palette.hue) else 1.75
                elif s.variant == Variant.VIBRANT:
                    return 1.36
            return 1.0

        color2025 = DynamicColor.from_palette(
            name="surfaceBright",
            palette=lambda s: s.neutral_palette,
            tone=_tone,
            is_background=True,
            chroma_multiplier=_chroma_multiplier,
        )
        return extend_spec_version(super().surfaceBright(), "2025", color2025)

    def surfaceContainerLowest(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="surfaceContainerLowest",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 0.0 if (s.is_dark or s.platform == "watch") else 100.0,
            is_background=True,
        )
        return extend_spec_version(
            super().surfaceContainerLowest(), "2025", color2025
        )

    def surfaceContainerLow(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "phone":
                if s.is_dark:
                    return 6.0
                else:
                    if Hct.is_yellow(s.neutral_palette.hue):
                        return 98.0
                    elif s.variant == Variant.VIBRANT:
                        return 95.0
                    else:
                        return 96.0
            else:
                return 15.0

        def _chroma_multiplier(s: "DynamicScheme") -> float:
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

        color2025 = DynamicColor.from_palette(
            name="surfaceContainerLow",
            palette=lambda s: s.neutral_palette,
            tone=_tone,
            is_background=True,
            chroma_multiplier=_chroma_multiplier,
        )
        return extend_spec_version(
            super().surfaceContainerLow(), "2025", color2025
        )

    def surfaceContainer(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "phone":
                if s.is_dark:
                    return 9.0
                else:
                    if Hct.is_yellow(s.neutral_palette.hue):
                        return 96.0
                    elif s.variant == Variant.VIBRANT:
                        return 92.0
                    else:
                        return 94.0
            else:
                return 20.0

        def _chroma_multiplier(s: "DynamicScheme") -> float:
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

        color2025 = DynamicColor.from_palette(
            name="surfaceContainer",
            palette=lambda s: s.neutral_palette,
            tone=_tone,
            is_background=True,
            chroma_multiplier=_chroma_multiplier,
        )
        return extend_spec_version(super().surfaceContainer(), "2025", color2025)

    def surfaceContainerHigh(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "phone":
                if s.is_dark:
                    return 12.0
                else:
                    if Hct.is_yellow(s.neutral_palette.hue):
                        return 94.0
                    elif s.variant == Variant.VIBRANT:
                        return 90.0
                    else:
                        return 92.0
            else:
                return 25.0

        def _chroma_multiplier(s: "DynamicScheme") -> float:
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

        color2025 = DynamicColor.from_palette(
            name="surfaceContainerHigh",
            palette=lambda s: s.neutral_palette,
            tone=_tone,
            is_background=True,
            chroma_multiplier=_chroma_multiplier,
        )
        return extend_spec_version(
            super().surfaceContainerHigh(), "2025", color2025
        )

    def surfaceContainerHighest(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.is_dark or s.platform == "watch":
                return 15.0
            else:
                if Hct.is_yellow(s.neutral_palette.hue):
                    return 92.0
                elif s.variant == Variant.VIBRANT:
                    return 88.0
                else:
                    return 90.0

        def _chroma_multiplier(s: "DynamicScheme") -> float:
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

        color2025 = DynamicColor.from_palette(
            name="surfaceContainerHighest",
            palette=lambda s: s.neutral_palette,
            tone=_tone,
            is_background=True,
            chroma_multiplier=_chroma_multiplier,
        )
        return extend_spec_version(
            super().surfaceContainerHighest(), "2025", color2025
        )

    def onSurface(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "phone" and s.variant == Variant.VIBRANT:
                return t_max_c(s.neutral_palette, 0, 100, 1.1)
            else:
                bg = (
                    self.highestSurface(s)
                    if s.platform == "phone"
                    else self.surfaceContainerHigh()
                )
                return DynamicColor.get_initial_tone_from_background(
                    lambda scheme: bg
                )(s)

        def _chroma_multiplier(s: "DynamicScheme") -> float:
            if s.platform == "phone":
                if s.variant == Variant.NEUTRAL:
                    return 2.2
                elif s.variant == Variant.TONAL_SPOT:
                    return 1.7
                elif s.variant == Variant.EXPRESSIVE:
                    return (
                        (3.0 if s.is_dark else 2.3)
                        if Hct.is_yellow(s.neutral_palette.hue)
                        else 1.6
                    )
            return 1.0

        color2025 = DynamicColor.from_palette(
            name="onSurface",
            palette=lambda s: s.neutral_palette,
            tone=_tone,
            chroma_multiplier=_chroma_multiplier,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                (get_curve(11) if s.is_dark else get_curve(9))
                if s.platform == "phone"
                else ContrastCurve(4.5, 9.0, 11.0, 21.0)
            ),
        )
        return extend_spec_version(super().onSurface(), "2025", color2025)

    def onSurfaceVariant(self) -> DynamicColor:
        def _chroma_multiplier(s: "DynamicScheme") -> float:
            if s.platform == "phone":
                if s.variant == Variant.NEUTRAL:
                    return 2.2
                elif s.variant == Variant.TONAL_SPOT:
                    return 1.7
                elif s.variant == Variant.EXPRESSIVE:
                    return (
                        (3.0 if s.is_dark else 2.3)
                        if Hct.is_yellow(s.neutral_palette.hue)
                        else 1.6
                    )
            return 1.0

        color2025 = DynamicColor.from_palette(
            name="onSurfaceVariant",
            palette=lambda s: (
                s.neutral_variant_palette
                if s.platform == "watch"
                else s.neutral_palette
            ),
            chroma_multiplier=_chroma_multiplier,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                (get_curve(6) if s.is_dark else get_curve(4.5))
                if s.platform == "phone"
                else ContrastCurve(3.0, 7.0, 7.0, 11.0)
            ),
        )
        return extend_spec_version(super().onSurfaceVariant(), "2025", color2025)

    def outline(self) -> DynamicColor:
        def _chroma_multiplier(s: "DynamicScheme") -> float:
            if s.platform == "phone":
                if s.variant == Variant.NEUTRAL:
                    return 2.2
                elif s.variant == Variant.TONAL_SPOT:
                    return 1.7
                elif s.variant == Variant.EXPRESSIVE:
                    return (
                        (3.0 if s.is_dark else 2.3)
                        if Hct.is_yellow(s.neutral_palette.hue)
                        else 1.6
                    )
            return 1.0

        color2025 = DynamicColor.from_palette(
            name="outline",
            palette=lambda s: (
                s.neutral_variant_palette
                if s.platform == "watch"
                else s.neutral_palette
            ),
            chroma_multiplier=_chroma_multiplier,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                get_curve(3)
                if s.platform == "phone"
                else ContrastCurve(1.5, 4.5, 4.5, 7.0)
            ),
        )
        return extend_spec_version(super().outline(), "2025", color2025)

    def outlineVariant(self) -> DynamicColor:
        def _chroma_multiplier(s: "DynamicScheme") -> float:
            if s.platform == "phone":
                if s.variant == Variant.NEUTRAL:
                    return 2.2
                elif s.variant == Variant.TONAL_SPOT:
                    return 1.7
                elif s.variant == Variant.EXPRESSIVE:
                    return (
                        (3.0 if s.is_dark else 2.3)
                        if Hct.is_yellow(s.neutral_palette.hue)
                        else 1.6
                    )
            return 1.0

        color2025 = DynamicColor.from_palette(
            name="outlineVariant",
            palette=lambda s: (
                s.neutral_variant_palette
                if s.platform == "watch"
                else s.neutral_palette
            ),
            chroma_multiplier=_chroma_multiplier,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                get_curve(1.5)
                if s.platform == "phone"
                else ContrastCurve(1.0, 3.0, 3.0, 4.5)
            ),
        )
        return extend_spec_version(super().outlineVariant(), "2025", color2025)

    def inverseSurface(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="inverseSurface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 98.0 if (s.is_dark or s.platform == "watch") else 4.0,
            is_background=True,
        )
        return extend_spec_version(super().inverseSurface(), "2025", color2025)

    def inverseOnSurface(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="inverseOnSurface",
            palette=lambda s: s.neutral_palette,
            background=lambda s: self.inverseSurface(),
            contrast_curve=lambda s: get_curve(7),
        )
        return extend_spec_version(super().inverseOnSurface(), "2025", color2025)

    def primary(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return (
                    90.0
                    if s.variant == Variant.NEUTRAL
                    else main_tone(
                        s.primary_palette,
                        90.0 if s.variant == Variant.TONAL_SPOT else 100.0,
                    )
                )
            elif s.variant == Variant.NEUTRAL:
                return 80.0 if s.is_dark else 40.0
            elif s.variant == Variant.TONAL_SPOT:
                return 80.0 if s.is_dark else t_max_c(s.primary_palette)
            elif s.variant == Variant.EXPRESSIVE:
                return t_max_c(
                    s.primary_palette,
                    0,
                    (
                        (88.0 if Hct.is_cyan(s.primary_palette.hue) else 98.0)
                        if s.is_dark
                        else (
                            25.0
                            if Hct.is_yellow(s.primary_palette.hue)
                            else 98.0
                        )
                    ),
                )
            else:  # VIBRANT
                return t_max_c(
                    s.primary_palette,
                    0,
                    88.0 if Hct.is_cyan(s.primary_palette.hue) else 98.0,
                )

        color2025 = DynamicColor.from_palette(
            name="primary",
            palette=lambda s: s.primary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                get_curve(4.5) if s.platform == "phone" else get_curve(7)
            ),
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
        return extend_spec_version(super().primary(), "2025", color2025)

    def primaryDim(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return (
                    85.0
                    if s.variant == Variant.NEUTRAL
                    else dim_tone(
                        s.primary_palette,
                        90.0 if s.variant == Variant.TONAL_SPOT else 100.0,
                    )
                )
            elif s.variant == Variant.NEUTRAL:
                return 85.0
            elif s.variant == Variant.TONAL_SPOT:
                return t_max_c(s.primary_palette, 0, 90.0)
            else:
                return t_max_c(s.primary_palette)

        color2025 = DynamicColor.from_palette(
            name="primaryDim",
            palette=lambda s: s.primary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: self.surfaceContainerHigh(),
            contrast_curve=lambda s: (
                ContrastCurve(4.5, 4.5, 4.5, 4.5)
                if s.platform == "watch"
                else get_curve(4.5)
            ),
            tone_delta_pair=lambda s: (
                None
                if s.platform == "watch"
                else ToneDeltaPair(
                    self.primaryDim(),
                    self.primary(),
                    5,
                    "darker",
                    True,
                    "farther",
                )
            ),
        )
        return color2025

    def onPrimary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onPrimary",
            palette=lambda s: s.primary_palette,
            background=lambda s: (
                self.primary() if s.platform == "phone" else self.primaryDim()
            ),
            contrast_curve=lambda s: (
                get_curve(6) if s.platform == "phone" else get_curve(7)
            ),
        )
        return extend_spec_version(super().onPrimary(), "2025", color2025)

    def primaryContainer(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return 30.0
            elif s.variant == Variant.NEUTRAL:
                return 30.0 if s.is_dark else 90.0
            elif s.variant == Variant.TONAL_SPOT:
                return (
                    t_min_c(s.primary_palette, 35, 93)
                    if s.is_dark
                    else t_max_c(s.primary_palette, 0, 90)
                )
            elif s.variant == Variant.EXPRESSIVE:
                return (
                    t_min_c(s.primary_palette, 30, 93)
                    if s.is_dark
                    else t_max_c(
                        s.primary_palette,
                        78,
                        88.0 if Hct.is_cyan(s.primary_palette.hue) else 90.0,
                    )
                )
            else:  # VIBRANT
                return (
                    t_min_c(s.primary_palette, 66, 93)
                    if s.is_dark
                    else t_max_c(
                        s.primary_palette,
                        66,
                        88.0 if Hct.is_cyan(s.primary_palette.hue) else 93.0,
                    )
                )

        color2025 = DynamicColor.from_palette(
            name="primaryContainer",
            palette=lambda s: s.primary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            tone_delta_pair=lambda s: (
                None
                if s.platform == "phone"
                else ToneDeltaPair(
                    self.primaryContainer(),
                    self.primaryDim(),
                    10,
                    "darker",
                    True,
                    "farther",
                )
            ),
            contrast_curve=lambda s: (
                (get_curve(1.5) if s.contrast_level > 0 else None)
                if s.platform == "phone"
                else ContrastCurve(1.0, 1.0, 3.0, 4.5)
            ),
        )
        return extend_spec_version(super().primaryContainer(), "2025", color2025)

    def onPrimaryContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onPrimaryContainer",
            palette=lambda s: s.primary_palette,
            background=lambda s: self.primaryContainer(),
            contrast_curve=lambda s: (
                get_curve(6)
                if s.platform == "phone"
                else ContrastCurve(3.0, 7.0, 7.0, 11.0)
            ),
        )
        return extend_spec_version(super().onPrimaryContainer(), "2025", color2025)

    def primaryFixed(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return (
                    90.0
                    if s.variant == Variant.NEUTRAL
                    else main_tone(
                        s.primary_palette,
                        90.0 if s.variant == Variant.TONAL_SPOT else 100.0,
                    )
                )
            temp_s = _temp_light_standard(s)
            return self.primaryContainer().get_tone(temp_s)

        color2025 = DynamicColor.from_palette(
            name="primaryFixed",
            palette=lambda s: s.primary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                (get_curve(1.5) if s.contrast_level > 0 else None)
                if s.platform == "phone"
                else ContrastCurve(7.0, 7.0, 7.0, 7.0)
            ),
        )
        return extend_spec_version(super().primaryFixed(), "2025", color2025)

    def primaryFixedDim(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return (
                    85.0
                    if s.variant == Variant.NEUTRAL
                    else dim_tone(
                        s.primary_palette,
                        90.0 if s.variant == Variant.TONAL_SPOT else 100.0,
                    )
                )
            return self.primaryFixed().get_tone(s)

        color2025 = DynamicColor.from_palette(
            name="primaryFixedDim",
            palette=lambda s: s.primary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.surfaceContainerHigh() if s.platform == "watch" else None
            ),
            contrast_curve=lambda s: (
                ContrastCurve(4.5, 4.5, 4.5, 4.5)
                if s.platform == "watch"
                else None
            ),
            tone_delta_pair=lambda s: (
                None
                if s.platform == "watch"
                else ToneDeltaPair(
                    self.primaryFixedDim(),
                    self.primaryFixed(),
                    5,
                    "darker",
                    True,
                    "exact",
                )
            ),
        )
        return extend_spec_version(super().primaryFixedDim(), "2025", color2025)

    def onPrimaryFixed(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onPrimaryFixed",
            palette=lambda s: s.primary_palette,
            background=lambda s: self.primaryFixedDim(),
            second_background=lambda s: (
                self.primaryFixed() if s.platform == "watch" else None
            ),
            contrast_curve=lambda s: (
                ContrastCurve(4.5, 7.0, 11.0, 21.0)
                if s.platform == "watch"
                else get_curve(7)
            ),
        )
        return extend_spec_version(super().onPrimaryFixed(), "2025", color2025)

    def onPrimaryFixedVariant(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return 30.0
            return DynamicColor.get_initial_tone_from_background(
                lambda scheme: self.primaryFixedDim()
            )(s)

        color2025 = DynamicColor.from_palette(
            name="onPrimaryFixedVariant",
            palette=lambda s: s.primary_palette,
            tone=_tone,
            background=lambda s: self.primaryFixedDim(),
            second_background=lambda s: (
                self.primaryFixed() if s.platform == "watch" else None
            ),
            contrast_curve=lambda s: (
                ContrastCurve(3.0, 4.5, 7.0, 11.0)
                if s.platform == "watch"
                else get_curve(4.5)
            ),
        )
        return extend_spec_version(
            super().onPrimaryFixedVariant(), "2025", color2025
        )

    def inversePrimary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="inversePrimary",
            palette=lambda s: s.primary_palette,
            tone=lambda s: t_max_c(s.primary_palette),
            background=lambda s: self.inverseSurface(),
            contrast_curve=lambda s: (
                get_curve(6) if s.platform == "phone" else get_curve(7)
            ),
        )
        return extend_spec_version(super().inversePrimary(), "2025", color2025)

    def secondary(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return (
                    90.0
                    if s.variant == Variant.NEUTRAL
                    else main_tone(s.secondary_palette, 90.0)
                )
            elif s.variant == Variant.NEUTRAL:
                return (
                    t_min_c(s.secondary_palette, 0, 98)
                    if s.is_dark
                    else t_max_c(s.secondary_palette)
                )
            elif s.variant == Variant.VIBRANT:
                return t_max_c(s.secondary_palette, 0, 90.0 if s.is_dark else 98.0)
            else:  # EXPRESSIVE and TONAL_SPOT
                return 80.0 if s.is_dark else t_max_c(s.secondary_palette)

        color2025 = DynamicColor.from_palette(
            name="secondary",
            palette=lambda s: s.secondary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                get_curve(4.5) if s.platform == "phone" else get_curve(7)
            ),
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
        return extend_spec_version(super().secondary(), "2025", color2025)

    def secondaryDim(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return (
                    85.0
                    if s.variant == Variant.NEUTRAL
                    else dim_tone(s.secondary_palette, 90.0)
                )
            elif s.variant == Variant.NEUTRAL:
                return 85.0
            else:
                return t_max_c(s.secondary_palette, 0, 90.0)

        color2025 = DynamicColor.from_palette(
            name="secondaryDim",
            palette=lambda s: s.secondary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: self.surfaceContainerHigh(),
            contrast_curve=lambda s: (
                ContrastCurve(4.5, 4.5, 4.5, 4.5)
                if s.platform == "watch"
                else get_curve(4.5)
            ),
            tone_delta_pair=lambda s: (
                None
                if s.platform == "watch"
                else ToneDeltaPair(
                    self.secondaryDim(),
                    self.secondary(),
                    5,
                    "darker",
                    True,
                    "farther",
                )
            ),
        )
        return color2025

    def onSecondary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onSecondary",
            palette=lambda s: s.secondary_palette,
            background=lambda s: (
                self.secondary() if s.platform == "phone" else self.secondaryDim()
            ),
            contrast_curve=lambda s: (
                get_curve(6) if s.platform == "phone" else get_curve(7)
            ),
        )
        return extend_spec_version(super().onSecondary(), "2025", color2025)

    def secondaryContainer(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return 30.0
            elif s.variant == Variant.VIBRANT:
                return (
                    t_min_c(s.secondary_palette, 30, 40)
                    if s.is_dark
                    else t_max_c(s.secondary_palette, 84, 90)
                )
            elif s.variant == Variant.EXPRESSIVE:
                return 15.0 if s.is_dark else t_max_c(s.secondary_palette, 90, 95)
            else:
                return 25.0 if s.is_dark else 90.0

        color2025 = DynamicColor.from_palette(
            name="secondaryContainer",
            palette=lambda s: s.secondary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            tone_delta_pair=lambda s: (
                ToneDeltaPair(
                    self.secondaryContainer(),
                    self.secondaryDim(),
                    10,
                    "darker",
                    True,
                    "farther",
                )
                if s.platform == "watch"
                else None
            ),
            contrast_curve=lambda s: (
                (get_curve(1.5) if s.contrast_level > 0 else None)
                if s.platform == "phone"
                else ContrastCurve(1.0, 1.0, 3.0, 4.5)
            ),
        )
        return extend_spec_version(super().secondaryContainer(), "2025", color2025)

    def onSecondaryContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onSecondaryContainer",
            palette=lambda s: s.secondary_palette,
            background=lambda s: self.secondaryContainer(),
            contrast_curve=lambda s: (
                get_curve(6)
                if s.platform == "phone"
                else ContrastCurve(3.0, 7.0, 7.0, 11.0)
            ),
        )
        return extend_spec_version(
            super().onSecondaryContainer(), "2025", color2025
        )

    def secondaryFixed(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return (
                    90.0
                    if s.variant == Variant.NEUTRAL
                    else main_tone(s.secondary_palette, 90.0)
                )
            temp_s = _temp_light_standard(s)
            return self.secondaryContainer().get_tone(temp_s)

        color2025 = DynamicColor.from_palette(
            name="secondaryFixed",
            palette=lambda s: s.secondary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                (get_curve(1.5) if s.contrast_level > 0 else None)
                if s.platform == "phone"
                else ContrastCurve(7.0, 7.0, 7.0, 7.0)
            ),
        )
        return extend_spec_version(super().secondaryFixed(), "2025", color2025)

    def secondaryFixedDim(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return (
                    85.0
                    if s.variant == Variant.NEUTRAL
                    else dim_tone(s.secondary_palette, 90.0)
                )
            return self.secondaryFixed().get_tone(s)

        color2025 = DynamicColor.from_palette(
            name="secondaryFixedDim",
            palette=lambda s: s.secondary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.surfaceContainerHigh() if s.platform == "watch" else None
            ),
            contrast_curve=lambda s: (
                ContrastCurve(4.5, 4.5, 4.5, 4.5)
                if s.platform == "watch"
                else None
            ),
            tone_delta_pair=lambda s: (
                None
                if s.platform == "watch"
                else ToneDeltaPair(
                    self.secondaryFixedDim(),
                    self.secondaryFixed(),
                    5,
                    "darker",
                    True,
                    "exact",
                )
            ),
        )
        return extend_spec_version(
            super().secondaryFixedDim(), "2025", color2025
        )

    def onSecondaryFixed(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onSecondaryFixed",
            palette=lambda s: s.secondary_palette,
            background=lambda s: self.secondaryFixedDim(),
            second_background=lambda s: (
                self.secondaryFixed() if s.platform == "watch" else None
            ),
            contrast_curve=lambda s: (
                ContrastCurve(4.5, 7.0, 11.0, 21.0)
                if s.platform == "watch"
                else get_curve(7)
            ),
        )
        return extend_spec_version(super().onSecondaryFixed(), "2025", color2025)

    def onSecondaryFixedVariant(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return 30.0
            return DynamicColor.get_initial_tone_from_background(
                lambda scheme: self.secondaryFixedDim()
            )(s)

        color2025 = DynamicColor.from_palette(
            name="onSecondaryFixedVariant",
            palette=lambda s: s.secondary_palette,
            tone=_tone,
            background=lambda s: self.secondaryFixedDim(),
            second_background=lambda s: (
                self.secondaryFixed() if s.platform == "watch" else None
            ),
            contrast_curve=lambda s: (
                ContrastCurve(3.0, 4.5, 7.0, 11.0)
                if s.platform == "watch"
                else get_curve(4.5)
            ),
        )
        return extend_spec_version(
            super().onSecondaryFixedVariant(), "2025", color2025
        )

    def tertiary(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return main_tone(
                    s.tertiary_palette,
                    90.0 if s.variant == Variant.TONAL_SPOT else 100.0,
                )
            elif (
                s.variant == Variant.EXPRESSIVE or s.variant == Variant.VIBRANT
            ):
                return t_max_c(
                    s.tertiary_palette,
                    0,
                    88.0
                    if Hct.is_cyan(s.tertiary_palette.hue)
                    else (98.0 if s.is_dark else 100.0),
                )
            else:  # NEUTRAL and TONAL_SPOT
                return (
                    t_max_c(s.tertiary_palette, 0, 98.0)
                    if s.is_dark
                    else t_max_c(s.tertiary_palette)
                )

        color2025 = DynamicColor.from_palette(
            name="tertiary",
            palette=lambda s: s.tertiary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                get_curve(4.5) if s.platform == "phone" else get_curve(7)
            ),
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
        return extend_spec_version(super().tertiary(), "2025", color2025)

    def tertiaryDim(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return dim_tone(
                    s.tertiary_palette,
                    90.0 if s.variant == Variant.TONAL_SPOT else 100.0,
                )
            elif s.variant == Variant.TONAL_SPOT:
                return t_max_c(s.tertiary_palette, 0, 90.0)
            else:
                return t_max_c(s.tertiary_palette)

        color2025 = DynamicColor.from_palette(
            name="tertiaryDim",
            palette=lambda s: s.tertiary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: self.surfaceContainerHigh(),
            contrast_curve=lambda s: (
                ContrastCurve(4.5, 4.5, 4.5, 4.5)
                if s.platform == "watch"
                else get_curve(4.5)
            ),
            tone_delta_pair=lambda s: (
                None
                if s.platform == "watch"
                else ToneDeltaPair(
                    self.tertiaryDim(),
                    self.tertiary(),
                    5,
                    "darker",
                    True,
                    "farther",
                )
            ),
        )
        return color2025

    def onTertiary(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onTertiary",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: (
                self.tertiary() if s.platform == "phone" else self.tertiaryDim()
            ),
            contrast_curve=lambda s: (
                get_curve(6) if s.platform == "phone" else get_curve(7)
            ),
        )
        return extend_spec_version(super().onTertiary(), "2025", color2025)

    def tertiaryContainer(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return container_tone(
                    s.tertiary_palette,
                    90.0 if s.variant == Variant.TONAL_SPOT else 100.0,
                )
            else:
                if s.variant == Variant.NEUTRAL:
                    return (
                        t_max_c(s.tertiary_palette, 0, 93.0)
                        if s.is_dark
                        else t_max_c(s.tertiary_palette, 0, 96.0)
                    )
                elif s.variant == Variant.TONAL_SPOT:
                    return t_max_c(
                        s.tertiary_palette, 0, 93.0 if s.is_dark else 100.0
                    )
                elif s.variant == Variant.EXPRESSIVE:
                    return t_max_c(
                        s.tertiary_palette,
                        75.0,
                        (
                            88.0
                            if Hct.is_cyan(s.tertiary_palette.hue)
                            else (93.0 if s.is_dark else 100.0)
                        ),
                    )
                else:  # VIBRANT
                    return (
                        t_max_c(s.tertiary_palette, 0, 93.0)
                        if s.is_dark
                        else t_max_c(s.tertiary_palette, 72.0, 100.0)
                    )

        color2025 = DynamicColor.from_palette(
            name="tertiaryContainer",
            palette=lambda s: s.tertiary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                (get_curve(1.5) if s.contrast_level > 0 else None)
                if s.platform == "phone"
                else ContrastCurve(1.0, 1.0, 3.0, 4.5)
            ),
        )
        return extend_spec_version(super().tertiaryContainer(), "2025", color2025)

    def onTertiaryContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onTertiaryContainer",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: self.tertiaryContainer(),
            contrast_curve=lambda s: (
                get_curve(6)
                if s.platform == "phone"
                else ContrastCurve(3.0, 7.0, 7.0, 11.0)
            ),
        )
        return extend_spec_version(
            super().onTertiaryContainer(), "2025", color2025
        )

    def tertiaryFixed(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return main_tone(
                    s.tertiary_palette,
                    90.0 if s.variant == Variant.TONAL_SPOT else 100.0,
                )
            temp_s = _temp_light_standard(s)
            return self.tertiaryContainer().get_tone(temp_s)

        color2025 = DynamicColor.from_palette(
            name="tertiaryFixed",
            palette=lambda s: s.tertiary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                (get_curve(1.5) if s.contrast_level > 0 else None)
                if s.platform == "phone"
                else ContrastCurve(7.0, 7.0, 7.0, 7.0)
            ),
        )
        return extend_spec_version(super().tertiaryFixed(), "2025", color2025)

    def tertiaryFixedDim(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return dim_tone(
                    s.tertiary_palette,
                    90.0 if s.variant == Variant.TONAL_SPOT else 100.0,
                )
            return self.tertiaryFixed().get_tone(s)

        color2025 = DynamicColor.from_palette(
            name="tertiaryFixedDim",
            palette=lambda s: s.tertiary_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.surfaceContainerHigh() if s.platform == "watch" else None
            ),
            contrast_curve=lambda s: (
                ContrastCurve(4.5, 4.5, 4.5, 4.5)
                if s.platform == "watch"
                else None
            ),
            tone_delta_pair=lambda s: (
                None
                if s.platform == "watch"
                else ToneDeltaPair(
                    self.tertiaryFixedDim(),
                    self.tertiaryFixed(),
                    5,
                    "darker",
                    True,
                    "exact",
                )
            ),
        )
        return extend_spec_version(
            super().tertiaryFixedDim(), "2025", color2025
        )

    def onTertiaryFixed(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onTertiaryFixed",
            palette=lambda s: s.tertiary_palette,
            background=lambda s: self.tertiaryFixedDim(),
            second_background=lambda s: (
                self.tertiaryFixed() if s.platform == "watch" else None
            ),
            contrast_curve=lambda s: (
                ContrastCurve(4.5, 7.0, 11.0, 21.0)
                if s.platform == "watch"
                else get_curve(7)
            ),
        )
        return extend_spec_version(super().onTertiaryFixed(), "2025", color2025)

    def onTertiaryFixedVariant(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return 30.0
            return DynamicColor.get_initial_tone_from_background(
                lambda scheme: self.tertiaryFixedDim()
            )(s)

        color2025 = DynamicColor.from_palette(
            name="onTertiaryFixedVariant",
            palette=lambda s: s.tertiary_palette,
            tone=_tone,
            background=lambda s: self.tertiaryFixedDim(),
            second_background=lambda s: (
                self.tertiaryFixed() if s.platform == "watch" else None
            ),
            contrast_curve=lambda s: (
                ContrastCurve(3.0, 4.5, 7.0, 11.0)
                if s.platform == "watch"
                else get_curve(4.5)
            ),
        )
        return extend_spec_version(
            super().onTertiaryFixedVariant(), "2025", color2025
        )

    def error(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "phone":
                return (
                    t_min_c(s.error_palette, 0, 98.0)
                    if s.is_dark
                    else t_max_c(s.error_palette)
                )
            else:
                starting_tone = DynamicColor.foreground_tone(25.0, 7.0)
                return find_desired_chroma_by_tone(
                    s.error_palette.hue,
                    s.error_palette.chroma,
                    starting_tone,
                    100.0,
                )

        color2025 = DynamicColor.from_palette(
            name="error",
            palette=lambda s: s.error_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            contrast_curve=lambda s: (
                get_curve(4.5)
                if s.platform == "phone"
                else ContrastCurve(3.0, 7.0, 7.0, 7.0)
            ),
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
        return extend_spec_version(super().error(), "2025", color2025)

    def errorDim(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
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
        return color2025

    def onError(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onError",
            palette=lambda s: s.error_palette,
            background=lambda s: (
                self.error() if s.platform == "phone" else self.errorDim()
            ),
            contrast_curve=lambda s: (
                get_curve(6)
                if s.platform == "phone"
                else ContrastCurve(4.5, 7.0, 11.0, 21.0)
            ),
        )
        return extend_spec_version(super().onError(), "2025", color2025)

    def errorContainer(self) -> DynamicColor:
        def _tone(s: "DynamicScheme") -> float:
            if s.platform == "watch":
                return 30.0
            else:
                return (
                    t_min_c(s.error_palette, 30, 93)
                    if s.is_dark
                    else t_max_c(s.error_palette, 0, 90)
                )

        color2025 = DynamicColor.from_palette(
            name="errorContainer",
            palette=lambda s: s.error_palette,
            tone=_tone,
            is_background=True,
            background=lambda s: (
                self.highestSurface(s)
                if s.platform == "phone"
                else self.surfaceContainerHigh()
            ),
            tone_delta_pair=lambda s: (
                ToneDeltaPair(
                    self.errorContainer(),
                    self.errorDim(),
                    10,
                    "darker",
                    True,
                    "farther",
                )
                if s.platform == "watch"
                else None
            ),
            contrast_curve=lambda s: (
                (get_curve(1.5) if s.contrast_level > 0 else None)
                if s.platform == "phone"
                else ContrastCurve(1.0, 1.0, 3.0, 4.5)
            ),
        )
        return extend_spec_version(super().errorContainer(), "2025", color2025)

    def onErrorContainer(self) -> DynamicColor:
        color2025 = DynamicColor.from_palette(
            name="onErrorContainer",
            palette=lambda s: s.error_palette,
            background=lambda s: self.errorContainer(),
            contrast_curve=lambda s: (
                get_curve(4.5)
                if s.platform == "phone"
                else ContrastCurve(3.0, 7.0, 7.0, 11.0)
            ),
        )
        return extend_spec_version(
            super().onErrorContainer(), "2025", color2025
        )

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
            lambda s: 100.0
            if s.platform == "watch"
            else self.onSurface().get_tone(s)
        )
        return extend_spec_version(super().onBackground(), "2025", color2025)
