from materialyoucolor.dislike.dislike_analyzer import DislikeAnalyzer
from materialyoucolor.dynamiccolor.color_spec import ColorSpecDelegate
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve
from materialyoucolor.dynamiccolor.dynamic_color import DynamicColor
from materialyoucolor.dynamiccolor.dynamic_scheme import DynamicScheme
from materialyoucolor.dynamiccolor.tone_delta_pair import ToneDeltaPair
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct


def is_fidelity(scheme: DynamicScheme) -> bool:
    return scheme.variant == Variant.FIDELITY or scheme.variant == Variant.CONTENT


def is_monochrome(scheme: DynamicScheme) -> bool:
    return scheme.variant == Variant.MONOCHROME


def find_desired_chroma_by_tone(
    hue: float, chroma: float, tone: float, by_decreasing_tone: bool
) -> float:
    answer = tone
    closest_to_chroma = Hct.from_hct(hue, chroma, tone)
    if closest_to_chroma.chroma < chroma:
        chroma_peak = closest_to_chroma.chroma
        while closest_to_chroma.chroma < chroma:
            answer += -1.0 if by_decreasing_tone else 1.0
            potential_solution = Hct.from_hct(hue, chroma, answer)
            if chroma_peak > potential_solution.chroma:
                break
            if abs(potential_solution.chroma - chroma) < 0.4:
                break
            if abs(potential_solution.chroma - chroma) < abs(
                closest_to_chroma.chroma - chroma
            ):
                closest_to_chroma = potential_solution
            chroma_peak = max(chroma_peak, potential_solution.chroma)
    return answer


class ColorSpecDelegateImpl2021(ColorSpecDelegate):
    def primaryPaletteKeyColor(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="primaryPaletteKeyColor",
            palette=lambda s: s.primary_palette,
            tone=lambda s: s.primary_palette.key_color.tone,
        )

    def secondaryPaletteKeyColor(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="secondaryPaletteKeyColor",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: s.secondary_palette.key_color.tone,
        )

    def tertiaryPaletteKeyColor(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="tertiaryPaletteKeyColor",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: s.tertiary_palette.key_color.tone,
        )

    def neutralPaletteKeyColor(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="neutralPaletteKeyColor",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: s.neutral_palette.key_color.tone,
        )

    def neutralVariantPaletteKeyColor(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="neutralVariantPaletteKeyColor",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: s.neutral_variant_palette.key_color.tone,
        )

    def errorPaletteKeyColor(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="errorPaletteKeyColor",
            palette=lambda s: s.error_palette,
            tone=lambda s: s.error_palette.key_color.tone,
        )

    def background(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="background",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 6 if s.is_dark else 98,
            is_background=True,
        )

    def onBackground(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onBackground",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 90 if s.is_dark else 10,
            background=lambda s: self.background(),
            contrast_curve=lambda s: ContrastCurve(3, 3, 4.5, 7),
        )

    def surface(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 6 if s.is_dark else 98,
            is_background=True,
        )

    def surfaceDim(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surfaceDim",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 6
            if s.is_dark
            else ContrastCurve(87, 87, 80, 75).get(s.contrast_level),
            is_background=True,
        )

    def surfaceBright(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surfaceBright",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: ContrastCurve(24, 24, 29, 34).get(s.contrast_level)
            if s.is_dark
            else 98,
            is_background=True,
        )

    def surfaceContainerLowest(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surfaceContainerLowest",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: ContrastCurve(4, 4, 2, 0).get(s.contrast_level)
            if s.is_dark
            else 100,
            is_background=True,
        )

    def surfaceContainerLow(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surfaceContainerLow",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: ContrastCurve(10, 10, 11, 12).get(s.contrast_level)
            if s.is_dark
            else ContrastCurve(96, 96, 96, 95).get(s.contrast_level),
            is_background=True,
        )

    def surfaceContainer(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surfaceContainer",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: ContrastCurve(12, 12, 16, 20).get(s.contrast_level)
            if s.is_dark
            else ContrastCurve(94, 94, 92, 90).get(s.contrast_level),
            is_background=True,
        )

    def surfaceContainerHigh(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surfaceContainerHigh",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: ContrastCurve(17, 17, 21, 25).get(s.contrast_level)
            if s.is_dark
            else ContrastCurve(92, 92, 88, 85).get(s.contrast_level),
            is_background=True,
        )

    def surfaceContainerHighest(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surfaceContainerHighest",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: ContrastCurve(22, 22, 26, 30).get(s.contrast_level)
            if s.is_dark
            else ContrastCurve(90, 90, 84, 80).get(s.contrast_level),
            is_background=True,
        )

    def onSurface(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onSurface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 90 if s.is_dark else 10,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(4.5, 7, 11, 21),
        )

    def surfaceVariant(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surfaceVariant",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: 30 if s.is_dark else 90,
            is_background=True,
        )

    def onSurfaceVariant(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onSurfaceVariant",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: 80 if s.is_dark else 30,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 11),
        )

    def inverseSurface(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="inverseSurface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 90 if s.is_dark else 20,
            is_background=True,
        )

    def inverseOnSurface(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="inverseOnSurface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 20 if s.is_dark else 95,
            background=lambda s: self.inverseSurface(),
            contrast_curve=lambda s: ContrastCurve(4.5, 7, 11, 21),
        )

    def outline(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="outline",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: 60 if s.is_dark else 50,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1.5, 3, 4.5, 7),
        )

    def outlineVariant(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="outlineVariant",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: 30 if s.is_dark else 80,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
        )

    def shadow(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="shadow",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 0,
        )

    def scrim(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="scrim",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 0,
        )

    def surfaceTint(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="surfaceTint",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 80 if s.is_dark else 40,
            is_background=True,
        )

    def primary(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="primary",
            palette=lambda s: s.primary_palette,
            tone=lambda s: (
                (100 if s.is_dark else 0)
                if is_monochrome(s)
                else (80 if s.is_dark else 40)
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 7),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.primaryContainer(), self.primary(), 10, "nearer", False
            ),
        )

    def primaryDim(self) -> DynamicColor:
        return None

    def onPrimary(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onPrimary",
            palette=lambda s: s.primary_palette,
            tone=lambda s: (
                (10 if s.is_dark else 90)
                if is_monochrome(s)
                else (20 if s.is_dark else 100)
            ),
            background=lambda s: self.primary(),
            contrast_curve=lambda s: ContrastCurve(4.5, 7, 11, 21),
        )

    def primaryContainer(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="primaryContainer",
            palette=lambda s: s.primary_palette,
            tone=lambda s: (
                s.source_color_hct.tone
                if is_fidelity(s)
                else (
                    (85 if s.is_dark else 25)
                    if is_monochrome(s)
                    else (30 if s.is_dark else 90)
                )
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.primaryContainer(), self.primary(), 10, "nearer", False
            ),
        )

    def onPrimaryContainer(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onPrimaryContainer",
            palette=lambda s: s.primary_palette,
            tone=lambda s: (
                DynamicColor.foreground_tone(self.primaryContainer().tone(s), 4.5)
                if is_fidelity(s)
                else (
                    (0 if s.is_dark else 100)
                    if is_monochrome(s)
                    else (90 if s.is_dark else 30)
                )
            ),
            background=lambda s: self.primaryContainer(),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 11),
        )

    def inversePrimary(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="inversePrimary",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 40 if s.is_dark else 80,
            background=lambda s: self.inverseSurface(),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 7),
        )

    def secondary(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="secondary",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 80 if s.is_dark else 40,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 7),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.secondaryContainer(), self.secondary(), 10, "nearer", False
            ),
        )

    def secondaryDim(self) -> DynamicColor:
        return None

    def onSecondary(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onSecondary",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: (
                (10 if s.is_dark else 100)
                if is_monochrome(s)
                else (20 if s.is_dark else 100)
            ),
            background=lambda s: self.secondary(),
            contrast_curve=lambda s: ContrastCurve(4.5, 7, 11, 21),
        )

    def secondaryContainer(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="secondaryContainer",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: (
                (30 if s.is_dark else 85)
                if is_monochrome(s)
                else (
                    find_desired_chroma_by_tone(
                        s.secondary_palette.hue,
                        s.secondary_palette.chroma,
                        30 if s.is_dark else 90,
                        not s.is_dark,
                    )
                    if is_fidelity(s)
                    else (30 if s.is_dark else 90)
                )
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.secondaryContainer(), self.secondary(), 10, "nearer", False
            ),
        )

    def onSecondaryContainer(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onSecondaryContainer",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: (
                (90 if s.is_dark else 10)
                if is_monochrome(s)
                else (
                    DynamicColor.foreground_tone(self.secondaryContainer().tone(s), 4.5)
                    if is_fidelity(s)
                    else (90 if s.is_dark else 30)
                )
            ),
            background=lambda s: self.secondaryContainer(),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 11),
        )

    def tertiary(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="tertiary",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: (
                (90 if s.is_dark else 25)
                if is_monochrome(s)
                else (80 if s.is_dark else 40)
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 7),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.tertiaryContainer(), self.tertiary(), 10, "nearer", False
            ),
        )

    def tertiaryDim(self) -> DynamicColor:
        return None

    def onTertiary(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onTertiary",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: (
                (10 if s.is_dark else 90)
                if is_monochrome(s)
                else (20 if s.is_dark else 100)
            ),
            background=lambda s: self.tertiary(),
            contrast_curve=lambda s: ContrastCurve(4.5, 7, 11, 21),
        )

    def tertiaryContainer(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="tertiaryContainer",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: (
                (60 if s.is_dark else 49)
                if is_monochrome(s)
                else (
                    DislikeAnalyzer.fix_if_disliked(
                        s.tertiary_palette.get_hct(s.source_color_hct.tone)
                    ).tone
                    if is_fidelity(s)
                    else (30 if s.is_dark else 90)
                )
            ),
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.tertiaryContainer(), self.tertiary(), 10, "nearer", False
            ),
        )

    def onTertiaryContainer(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onTertiaryContainer",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: (
                (0 if s.is_dark else 100)
                if is_monochrome(s)
                else (
                    DynamicColor.foreground_tone(self.tertiaryContainer().tone(s), 4.5)
                    if is_fidelity(s)
                    else (90 if s.is_dark else 30)
                )
            ),
            background=lambda s: self.tertiaryContainer(),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 11),
        )

    def error(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="error",
            palette=lambda s: s.error_palette,
            tone=lambda s: 80 if s.is_dark else 40,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 7),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.errorContainer(), self.error(), 10, "nearer", False
            ),
        )

    def errorDim(self) -> DynamicColor:
        return None

    def onError(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onError",
            palette=lambda s: s.error_palette,
            tone=lambda s: 20 if s.is_dark else 100,
            background=lambda s: self.error(),
            contrast_curve=lambda s: ContrastCurve(4.5, 7, 11, 21),
        )

    def errorContainer(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="errorContainer",
            palette=lambda s: s.error_palette,
            tone=lambda s: 30 if s.is_dark else 90,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.errorContainer(), self.error(), 10, "nearer", False
            ),
        )

    def onErrorContainer(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onErrorContainer",
            palette=lambda s: s.error_palette,
            tone=lambda s: (
                (90 if s.is_dark else 10)
                if is_monochrome(s)
                else (90 if s.is_dark else 30)
            ),
            background=lambda s: self.errorContainer(),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 11),
        )

    def primaryFixed(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="primaryFixed",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 40.0 if is_monochrome(s) else 90.0,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.primaryFixed(), self.primaryFixedDim(), 10, "lighter", True
            ),
        )

    def primaryFixedDim(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="primaryFixedDim",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 30.0 if is_monochrome(s) else 80.0,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.primaryFixed(), self.primaryFixedDim(), 10, "lighter", True
            ),
        )

    def onPrimaryFixed(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onPrimaryFixed",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 100.0 if is_monochrome(s) else 10.0,
            background=lambda s: self.primaryFixedDim(),
            second_background=lambda s: self.primaryFixed(),
            contrast_curve=lambda s: ContrastCurve(4.5, 7, 11, 21),
        )

    def onPrimaryFixedVariant(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onPrimaryFixedVariant",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 90.0 if is_monochrome(s) else 30.0,
            background=lambda s: self.primaryFixedDim(),
            second_background=lambda s: self.primaryFixed(),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 11),
        )

    def secondaryFixed(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="secondaryFixed",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 80.0 if is_monochrome(s) else 90.0,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.secondaryFixed(), self.secondaryFixedDim(), 10, "lighter", True
            ),
        )

    def secondaryFixedDim(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="secondaryFixedDim",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 70.0 if is_monochrome(s) else 80.0,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.secondaryFixed(), self.secondaryFixedDim(), 10, "lighter", True
            ),
        )

    def onSecondaryFixed(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onSecondaryFixed",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 10.0,
            background=lambda s: self.secondaryFixedDim(),
            second_background=lambda s: self.secondaryFixed(),
            contrast_curve=lambda s: ContrastCurve(4.5, 7, 11, 21),
        )

    def onSecondaryFixedVariant(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onSecondaryFixedVariant",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 25.0 if is_monochrome(s) else 30.0,
            background=lambda s: self.secondaryFixedDim(),
            second_background=lambda s: self.secondaryFixed(),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 11),
        )

    def tertiaryFixed(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="tertiaryFixed",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: 40.0 if is_monochrome(s) else 90.0,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.tertiaryFixed(), self.tertiaryFixedDim(), 10, "lighter", True
            ),
        )

    def tertiaryFixedDim(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="tertiaryFixedDim",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: 30.0 if is_monochrome(s) else 80.0,
            is_background=True,
            background=lambda s: self.highestSurface(s),
            contrast_curve=lambda s: ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                self.tertiaryFixed(), self.tertiaryFixedDim(), 10, "lighter", True
            ),
        )

    def onTertiaryFixed(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onTertiaryFixed",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: 100.0 if is_monochrome(s) else 10.0,
            background=lambda s: self.tertiaryFixedDim(),
            second_background=lambda s: self.tertiaryFixed(),
            contrast_curve=lambda s: ContrastCurve(4.5, 7, 11, 21),
        )

    def onTertiaryFixedVariant(self) -> DynamicColor:
        return DynamicColor.from_palette(
            name="onTertiaryFixedVariant",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: 90.0 if is_monochrome(s) else 30.0,
            background=lambda s: self.tertiaryFixedDim(),
            second_background=lambda s: self.tertiaryFixed(),
            contrast_curve=lambda s: ContrastCurve(3, 4.5, 7, 11),
        )

    def highestSurface(self, s: DynamicScheme) -> DynamicColor:
        return self.surfaceBright() if s.is_dark else self.surfaceDim()
