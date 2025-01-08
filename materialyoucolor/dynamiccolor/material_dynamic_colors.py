from materialyoucolor.hct import Hct
from materialyoucolor.scheme.dynamic_scheme import DynamicScheme
from materialyoucolor.scheme.variant import Variant
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve
from materialyoucolor.dynamiccolor.tone_delta_pair import ToneDeltaPair
from materialyoucolor.dynamiccolor.dynamic_color import FromPaletteOptions, DynamicColor
from materialyoucolor.dislike.dislike_analyzer import DislikeAnalyzer


def is_fidelity(scheme: DynamicScheme) -> bool:
    return scheme.variant == Variant.FIDELITY or scheme.variant == Variant.CONTENT


def is_monochrome(scheme: DynamicScheme) -> bool:
    return scheme.variant == Variant.MONOCHROME


def find_desired_chroma_by_tone(
    hue: float, chroma: float, tone: float, by_decreasing_tone: float
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

            potential_delta = abs(potential_solution.chroma - chroma)
            current_delta = abs(closest_to_chroma.chroma - chroma)
            if potential_delta < current_delta:
                closest_to_chroma = potential_solution
            chroma_peak = max(chroma_peak, potential_solution.chroma)

    return answer


def secondary_container_tone(s):
    initial_tone = 30 if s.is_dark else 90
    if is_monochrome(s):
        return 30 if s.is_dark else 85
    if is_fidelity(s):
        return initial_tone
    return find_desired_chroma_by_tone(
        s.secondary_palette.hue,
        s.secondary_palette.chroma,
        initial_tone,
        False if s.is_dark else True,
    )


def on_secondary_container_tone(s):
    if is_monochrome(s):
        return 90 if s.is_dark else 10
    if not is_fidelity(s):
        return 90 if s.is_dark else 30
    return DynamicColor.foreground_tone(
        MaterialDynamicColors.secondaryContainer.tone(s), 4.5
    )


def tertiary_container_tone(s):
    if not is_monochrome(s):
        return 60 if s.is_dark else 49
    if not is_fidelity(s):
        return 30 if s.is_dark else 90
    proposed_hct = s.tertiary_palette.get_hct(s.source_color_hct.tone)
    return DislikeAnalyzer.fix_if_disliked(proposed_hct).tone


def on_tertiary_container_tone(s):
    if not is_monochrome(s):
        return 0 if s.is_dark else 100
    if not is_fidelity(s):
        return 90 if s.is_dark else 30
    return DynamicColor.foreground_tone(
        MaterialDynamicColors.tertiaryContainer.tone(s), 4.5
    )


class MaterialDynamicColors:
    content_accent_tone_delta = 15.0

    @staticmethod
    def highestSurface(s: DynamicScheme) -> DynamicColor:
        return (
            MaterialDynamicColors.surfaceBright
            if s.is_dark
            else MaterialDynamicColors.surfaceDim
        )

    primary_paletteKeyColor = DynamicColor.from_palette(
        FromPaletteOptions(
            name="primary_palette_key_color",
            palette=lambda s: s.primary_palette,
            tone=lambda s: s.primary_palette.key_color.tone,
        )
    )

    secondary_paletteKeyColor = DynamicColor.from_palette(
        FromPaletteOptions(
            name="secondary_palette_key_color",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: s.secondary_palette.key_color.tone,
        )
    )

    tertiary_paletteKeyColor = DynamicColor.from_palette(
        FromPaletteOptions(
            name="tertiary_palette_key_color",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: s.tertiary_palette.key_color.tone,
        )
    )

    neutral_paletteKeyColor = DynamicColor.from_palette(
        FromPaletteOptions(
            name="neutral_palette_key_color",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: s.neutral_palette.key_color.tone,
        )
    )

    neutral_variant_paletteKeyColor = DynamicColor.from_palette(
        FromPaletteOptions(
            name="neutral_variant_palette_key_color",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: s.neutral_variant_palette.key_color.tone,
        )
    )

    background = DynamicColor.from_palette(
        FromPaletteOptions(
            name="background",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 6 if s.is_dark else 98,
            is_background=True,
        )
    )

    onBackground = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_background",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 90 if s.is_dark else 10,
            background=lambda s: MaterialDynamicColors.background,
            contrast_curve=ContrastCurve(3, 3, 4.5, 7),
        )
    )

    surface = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 6 if s.is_dark else 98,
            is_background=True,
        )
    )

    surfaceDim = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface_dim",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (
                6 if s.is_dark else ContrastCurve(87, 87, 80, 75).get(s.contrast_level)
            ),
            is_background=True,
        )
    )

    surfaceBright = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface_bright",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (
                ContrastCurve(24, 24, 29, 34).get(s.contrast_level) if s.is_dark else 98
            ),
            is_background=True,
        )
    )

    surfaceContainerLowest = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface_container_lowest",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (
                ContrastCurve(4, 4, 2, 0).get(s.contrast_level) if s.is_dark else 100
            ),
            is_background=True,
        )
    )

    surfaceContainerLow = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface_container_low",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (
                ContrastCurve(10, 10, 11, 12).get(s.contrast_level)
                if s.is_dark
                else ContrastCurve(96, 96, 96, 95).get(s.contrast_level)
            ),
            is_background=True,
        )
    )

    surfaceContainer = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface_container",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (
                ContrastCurve(12, 12, 16, 20).get(s.contrast_level)
                if s.is_dark
                else ContrastCurve(94, 94, 92, 90).get(s.contrast_level)
            ),
            is_background=True,
        )
    )

    surfaceContainerHigh = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface_container_high",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (
                ContrastCurve(17, 17, 21, 25).get(s.contrast_level)
                if s.is_dark
                else ContrastCurve(92, 92, 88, 85).get(s.contrast_level)
            ),
            is_background=True,
        )
    )

    surfaceContainerHighest = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface_container_highest",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: (
                ContrastCurve(22, 22, 26, 30).get(s.contrast_level)
                if s.is_dark
                else ContrastCurve(90, 90, 84, 80).get(s.contrast_level)
            ),
            is_background=True,
        )
    )

    onSurface = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_surface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 90 if s.is_dark else 10,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(4.5, 7, 11, 21),
        )
    )

    surfaceVariant = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface_variant",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: 30 if s.is_dark else 90,
            is_background=True,
        )
    )

    onSurfaceVariant = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_surface_variant",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: 80 if s.is_dark else 30,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(3, 4.5, 7, 11),
        )
    )

    inverseSurface = DynamicColor.from_palette(
        FromPaletteOptions(
            name="inverse_surface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 90 if s.is_dark else 20,
        )
    )

    inverseOnSurface = DynamicColor.from_palette(
        FromPaletteOptions(
            name="inverse_on_surface",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 20 if s.is_dark else 95,
            background=lambda s: MaterialDynamicColors.inverseSurface,
            contrast_curve=ContrastCurve(4.5, 7, 11, 21),
        )
    )

    outline = DynamicColor.from_palette(
        FromPaletteOptions(
            name="outline",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: 60 if s.is_dark else 50,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1.5, 3, 4.5, 7),
        )
    )

    outlineVariant = DynamicColor.from_palette(
        FromPaletteOptions(
            name="outline_variant",
            palette=lambda s: s.neutral_variant_palette,
            tone=lambda s: 30 if s.is_dark else 80,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
        )
    )

    shadow = DynamicColor.from_palette(
        FromPaletteOptions(
            name="shadow",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 0,
        )
    )

    scrim = DynamicColor.from_palette(
        FromPaletteOptions(
            name="scrim",
            palette=lambda s: s.neutral_palette,
            tone=lambda s: 0,
        )
    )

    surfaceTint = DynamicColor.from_palette(
        FromPaletteOptions(
            name="surface_tint",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 80 if s.is_dark else 40,
            is_background=True,
        )
    )

    primary = DynamicColor.from_palette(
        FromPaletteOptions(
            name="primary",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 100 if is_monochrome(s) else (80 if s.is_dark else 40),
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(3, 4.5, 7, 7),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.primaryContainer,
                MaterialDynamicColors.primary,
                10,
                "nearer",
                False,
            ),
        )
    )

    onPrimary = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_primary",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 10 if is_monochrome(s) else (20 if s.is_dark else 100),
            background=lambda s: MaterialDynamicColors.primary,
            contrast_curve=ContrastCurve(4.5, 7, 11, 21),
        )
    )

    primaryContainer = DynamicColor.from_palette(
        FromPaletteOptions(
            name="primary_container",
            palette=lambda s: s.primary_palette,
            tone=lambda s: (
                s.source_color_hct.tone
                if is_fidelity(s)
                else (85 if is_monochrome(s) else (30 if s.is_dark else 90))
            ),
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.primaryContainer,
                MaterialDynamicColors.primary,
                10,
                "nearer",
                False,
            ),
        )
    )

    onPrimaryContainer = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_primary_container",
            palette=lambda s: s.primary_palette,
            tone=lambda s: (
                DynamicColor.foreground_tone(
                    MaterialDynamicColors.primaryContainer.tone(s), 4.5
                )
                if is_fidelity(s)
                else (0 if is_monochrome(s) else (90 if s.is_dark else 30))
            ),
            background=lambda s: MaterialDynamicColors.primaryContainer,
            contrast_curve=ContrastCurve(3, 4.5, 7, 11),
        )
    )

    inversePrimary = DynamicColor.from_palette(
        FromPaletteOptions(
            name="inverse_primary",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 40 if s.is_dark else 80,
            background=lambda s: MaterialDynamicColors.inverseSurface,
            contrast_curve=ContrastCurve(3, 4.5, 7, 7),
        )
    )

    secondary = DynamicColor.from_palette(
        FromPaletteOptions(
            name="secondary",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 80 if s.is_dark else 40,
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(3, 4.5, 7, 7),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.secondaryContainer,
                MaterialDynamicColors.secondary,
                10,
                "nearer",
                False,
            ),
        )
    )

    onSecondary = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_secondary",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 10 if is_monochrome(s) else (20 if s.is_dark else 100),
            background=lambda s: MaterialDynamicColors.secondary,
            contrast_curve=ContrastCurve(4.5, 7, 11, 21),
        )
    )

    secondaryContainer = DynamicColor.from_palette(
        FromPaletteOptions(
            name="secondary_container",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: secondary_container_tone(s),
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.secondaryContainer,
                MaterialDynamicColors.secondary,
                10,
                "nearer",
                False,
            ),
        )
    )

    onSecondaryContainer = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_secondary_container",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: on_secondary_container_tone(s),
            background=lambda s: MaterialDynamicColors.secondaryContainer,
            contrast_curve=ContrastCurve(3.0, 4.5, 7, 11),
        )
    )

    tertiary = DynamicColor.from_palette(
        FromPaletteOptions(
            name="tertiary",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: (
                (90 if s.is_dark else 25)
                if is_monochrome(s)
                else (80 if s.is_dark else 40)
            ),
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(3, 4.5, 7, 7),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.tertiaryContainer,
                MaterialDynamicColors.tertiary,
                10,
                "nearer",
                False,
            ),
        )
    )

    onTertiary = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_tertiary",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: (
                (10 if s.is_dark else 90)
                if is_monochrome(s)
                else (20 if s.is_dark else 100)
            ),
            background=lambda s: MaterialDynamicColors.tertiary,
            contrast_curve=ContrastCurve(4.5, 7, 11, 21),
        )
    )

    tertiaryContainer = DynamicColor.from_palette(
        FromPaletteOptions(
            name="tertiary_container",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: tertiary_container_tone(s),
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.tertiaryContainer,
                MaterialDynamicColors.tertiary,
                10,
                "nearer",
                False,
            ),
        )
    )

    onTertiaryContainer = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_tertiary_container",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: on_tertiary_container_tone(s),
            background=lambda s: MaterialDynamicColors.tertiaryContainer,
            contrast_curve=ContrastCurve(3.0, 4.5, 7, 11),
        )
    )

    error = DynamicColor.from_palette(
        FromPaletteOptions(
            name="error",
            palette=lambda s: s.error_palette,
            tone=lambda s: 80 if s.is_dark else 40,
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(3, 4.5, 7, 7),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.errorContainer,
                MaterialDynamicColors.error,
                10,
                "nearer",
                False,
            ),
        )
    )

    onError = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_error",
            palette=lambda s: s.error_palette,
            tone=lambda s: 20 if s.is_dark else 100,
            background=lambda s: MaterialDynamicColors.error,
            contrast_curve=ContrastCurve(4.5, 7, 11, 21),
        )
    )

    errorContainer = DynamicColor.from_palette(
        FromPaletteOptions(
            name="error_container",
            palette=lambda s: s.error_palette,
            tone=lambda s: 30 if s.is_dark else 90,
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.errorContainer,
                MaterialDynamicColors.error,
                10,
                "nearer",
                False,
            ),
        )
    )

    onErrorContainer = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_error_container",
            palette=lambda s: s.error_palette,
            tone=lambda s: 90 if s.is_dark else (10 if is_monochrome(s) else 30),
            background=lambda s: MaterialDynamicColors.errorContainer,
            contrast_curve=ContrastCurve(3.0, 4.5, 7, 11),
        )
    )

    primaryFixed = DynamicColor.from_palette(
        FromPaletteOptions(
            name="primary_fixed",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 40.0 if is_monochrome(s) else 90.0,
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.primaryFixed,
                MaterialDynamicColors.primaryFixedDim,
                10,
                "lighter",
                True,
            ),
        )
    )

    primaryFixedDim = DynamicColor.from_palette(
        FromPaletteOptions(
            name="primary_fixed_dim",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 30.0 if is_monochrome(s) else 80.0,
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.primaryFixed,
                MaterialDynamicColors.primaryFixedDim,
                10,
                "lighter",
                True,
            ),
        )
    )

    onPrimaryFixed = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_primary_fixed",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 100.0 if is_monochrome(s) else 10.0,
            background=lambda s: MaterialDynamicColors.primaryFixedDim,
            second_background=lambda s: MaterialDynamicColors.primaryFixed,
            contrast_curve=ContrastCurve(4.5, 7, 11, 21),
        )
    )

    onPrimaryFixedVariant = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_primary_fixed_variant",
            palette=lambda s: s.primary_palette,
            tone=lambda s: 90.0 if is_monochrome(s) else 30.0,
            background=lambda s: MaterialDynamicColors.primaryFixedDim,
            second_background=lambda s: MaterialDynamicColors.primaryFixed,
            contrast_curve=ContrastCurve(3, 4.5, 7, 11),
        )
    )

    secondaryFixed = DynamicColor.from_palette(
        FromPaletteOptions(
            name="secondary_fixed",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 80.0 if is_monochrome(s) else 90.0,
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.secondaryFixed,
                MaterialDynamicColors.secondaryFixedDim,
                10,
                "lighter",
                True,
            ),
        )
    )

    secondaryFixedDim = DynamicColor.from_palette(
        FromPaletteOptions(
            name="secondary_fixed_dim",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 70.0 if is_monochrome(s) else 80.0,
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.secondaryFixed,
                MaterialDynamicColors.secondaryFixedDim,
                10,
                "lighter",
                True,
            ),
        )
    )

    onSecondaryFixed = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_secondary_fixed",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 10.0,
            background=lambda s: MaterialDynamicColors.secondaryFixedDim,
            second_background=lambda s: MaterialDynamicColors.secondaryFixed,
            contrast_curve=ContrastCurve(4.5, 7, 11, 21),
        )
    )

    onSecondaryFixedVariant = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_secondary_fixed_variant",
            palette=lambda s: s.secondary_palette,
            tone=lambda s: 25.0 if is_monochrome(s) else 30.0,
            background=lambda s: MaterialDynamicColors.secondaryFixedDim,
            second_background=lambda s: MaterialDynamicColors.secondaryFixed,
            contrast_curve=ContrastCurve(3, 4.5, 7, 11),
        )
    )

    tertiaryFixed = DynamicColor.from_palette(
        FromPaletteOptions(
            name="tertiary_fixed",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: 40.0 if is_monochrome(s) else 90.0,
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.tertiaryFixed,
                MaterialDynamicColors.tertiaryFixedDim,
                10,
                "lighter",
                True,
            ),
        )
    )

    tertiaryFixedDim = DynamicColor.from_palette(
        FromPaletteOptions(
            name="tertiary_fixed_dim",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: 30.0 if is_monochrome(s) else 80.0,
            is_background=True,
            background=lambda s: MaterialDynamicColors.highestSurface(s),
            contrast_curve=ContrastCurve(1, 1, 3, 4.5),
            tone_delta_pair=lambda s: ToneDeltaPair(
                MaterialDynamicColors.tertiaryFixed,
                MaterialDynamicColors.tertiaryFixedDim,
                10,
                "lighter",
                True,
            ),
        )
    )

    onTertiaryFixed = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_tertiary_fixed",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: 100.0 if is_monochrome(s) else 10.0,
            background=lambda s: MaterialDynamicColors.tertiaryFixedDim,
            second_background=lambda s: MaterialDynamicColors.tertiaryFixed,
            contrast_curve=ContrastCurve(4.5, 7, 11, 21),
        )
    )

    onTertiaryFixedVariant = DynamicColor.from_palette(
        FromPaletteOptions(
            name="on_tertiary_fixed_variant",
            palette=lambda s: s.tertiary_palette,
            tone=lambda s: 90.0 if is_monochrome(s) else 30.0,
            background=lambda s: MaterialDynamicColors.tertiaryFixedDim,
            second_background=lambda s: MaterialDynamicColors.tertiaryFixed,
            contrast_curve=ContrastCurve(3, 4.5, 7, 11),
        )
    )
