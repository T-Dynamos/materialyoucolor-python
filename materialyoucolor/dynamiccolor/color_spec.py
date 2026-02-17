from abc import ABC, abstractmethod
from typing import Literal

from materialyoucolor.contrast.contrast import Contrast
from materialyoucolor.hct.hct import Hct
from materialyoucolor.utils.math_utils import clamp_double

SpecVersion = Literal["2021", "2025"]

COLOR_NAMES = [
    # Background & surface base
    "background",
    "onBackground",
    "surface",
    "surfaceDim",
    "surfaceBright",
    # Surface containers (elevation scale)
    "surfaceContainerLowest",
    "surfaceContainerLow",
    "surfaceContainer",
    "surfaceContainerHigh",
    "surfaceContainerHighest",
    # Surface content
    "onSurface",
    "surfaceVariant",
    "onSurfaceVariant",
    # Outlines & effects
    "outline",
    "outlineVariant",
    "inverseSurface",
    "inverseOnSurface",
    "shadow",
    "scrim",
    "surfaceTint",
    # Primary colors
    "primary",
    "primaryDim",
    "onPrimary",
    "primaryContainer",
    "onPrimaryContainer",
    "inversePrimary",
    "primaryFixed",
    "primaryFixedDim",
    "onPrimaryFixed",
    "onPrimaryFixedVariant",
    # Secondary colors
    "secondary",
    "secondaryDim",
    "onSecondary",
    "secondaryContainer",
    "onSecondaryContainer",
    "secondaryFixed",
    "secondaryFixedDim",
    "onSecondaryFixed",
    "onSecondaryFixedVariant",
    # Tertiary colors
    "tertiary",
    "tertiaryDim",
    "onTertiary",
    "tertiaryContainer",
    "onTertiaryContainer",
    "tertiaryFixed",
    "tertiaryFixedDim",
    "onTertiaryFixed",
    "onTertiaryFixedVariant",
    # Error colors
    "error",
    "errorDim",
    "onError",
    "errorContainer",
    "onErrorContainer",
    # Palette key colors
    "primaryPaletteKeyColor",
    "secondaryPaletteKeyColor",
    "tertiaryPaletteKeyColor",
    "neutralPaletteKeyColor",
    "neutralVariantPaletteKeyColor",
    "errorPaletteKeyColor",
]


class ColorSpecDelegate(ABC):
    """
    A delegate that provides the dynamic color constraints for
    MaterialDynamicColors.

    This is used to allow for different color constraints for different spec
    versions.
    """

    # define them dynamically
    for color_name in COLOR_NAMES:
        exec(
            f"@abstractmethod\ndef {color_name}(self) -> 'DynamicColor':\n\treturn None"
        )

    # Other
    @abstractmethod
    def highestSurface(self, s: "DynamicScheme") -> "DynamicColor":
        pass


_spec_2021 = None
_spec_2025 = None


def get_spec(spec_version: SpecVersion) -> ColorSpecDelegate:
    global _spec_2021, _spec_2025
    if spec_version == "2021":
        if _spec_2021 is None:
            from materialyoucolor.dynamiccolor.color_spec_2021 import (
                ColorSpecDelegateImpl2021,
            )

            _spec_2021 = ColorSpecDelegateImpl2021()
        return _spec_2021
    elif spec_version == "2025":
        if _spec_2025 is None:
            from materialyoucolor.dynamiccolor.color_spec_2025 import (
                ColorSpecDelegateImpl2025,
            )

            _spec_2025 = ColorSpecDelegateImpl2025()
        return _spec_2025
    else:
        raise ValueError(f"Unsupported spec version: {spec_version}")


class ColorCalculationDelegate:
    def get_hct(self, scheme: "DynamicScheme", color: "DynamicColor") -> "Hct":
        raise NotImplementedError

    def get_tone(self, scheme: "DynamicScheme", color: "DynamicColor") -> float:
        raise NotImplementedError


class ColorCalculationDelegateImpl2021(ColorCalculationDelegate):
    def get_hct(self, scheme: "DynamicScheme", color: "DynamicColor") -> "Hct":
        tone = color.get_tone(scheme)
        palette = color.palette(scheme)
        return palette.get_hct(tone)

    def get_tone(self, scheme: "DynamicScheme", color: "DynamicColor") -> float:
        from materialyoucolor.dynamiccolor.dynamic_color import DynamicColor

        decreasing_contrast = scheme.contrast_level < 0
        tone_delta_pair = (
            color.tone_delta_pair(scheme) if color.tone_delta_pair else None
        )

        if tone_delta_pair:
            role_a = tone_delta_pair.role_a
            role_b = tone_delta_pair.role_b
            delta = tone_delta_pair.delta
            polarity = tone_delta_pair.polarity
            stay_together = tone_delta_pair.stay_together

            a_is_nearer = (
                polarity == "nearer"
                or (polarity == "lighter" and not scheme.is_dark)
                or (polarity == "darker" and scheme.is_dark)
            )
            nearer = role_a if a_is_nearer else role_b
            farther = role_b if a_is_nearer else role_a
            am_nearer = color.name == nearer.name
            expansion_dir = 1 if scheme.is_dark else -1
            n_tone = nearer.tone(scheme)
            f_tone = farther.tone(scheme)

            if color.background and nearer.contrast_curve and farther.contrast_curve:
                bg = color.background(scheme)
                n_contrast_curve = nearer.contrast_curve(scheme)
                f_contrast_curve = farther.contrast_curve(scheme)
                if bg and n_contrast_curve and f_contrast_curve:
                    bg_tone = bg.get_tone(scheme)
                    n_contrast = n_contrast_curve.get(scheme.contrast_level)
                    f_contrast = f_contrast_curve.get(scheme.contrast_level)

                    if Contrast.ratio_of_tones(bg_tone, n_tone) < n_contrast:
                        n_tone = DynamicColor.foreground_tone(bg_tone, n_contrast)
                    if Contrast.ratio_of_tones(bg_tone, f_tone) < f_contrast:
                        f_tone = DynamicColor.foreground_tone(bg_tone, f_contrast)
                    if decreasing_contrast:
                        n_tone = DynamicColor.foreground_tone(bg_tone, n_contrast)
                        f_tone = DynamicColor.foreground_tone(bg_tone, f_contrast)

            if (f_tone - n_tone) * expansion_dir < delta:
                f_tone = clamp_double(0, 100, n_tone + delta * expansion_dir)
                if (f_tone - n_tone) * expansion_dir >= delta:
                    pass
                else:
                    n_tone = clamp_double(0, 100, f_tone - delta * expansion_dir)

            if 50 <= n_tone < 60:
                if expansion_dir > 0:
                    n_tone = 60
                    f_tone = max(f_tone, n_tone + delta * expansion_dir)
                else:
                    n_tone = 49
                    f_tone = min(f_tone, n_tone + delta * expansion_dir)
            elif 50 <= f_tone < 60:
                if stay_together:
                    if expansion_dir > 0:
                        n_tone = 60
                        f_tone = max(f_tone, n_tone + delta * expansion_dir)
                    else:
                        n_tone = 49
                        f_tone = min(f_tone, n_tone + delta * expansion_dir)
                else:
                    if expansion_dir > 0:
                        f_tone = 60
                    else:
                        f_tone = 49
            return n_tone if am_nearer else f_tone
        else:
            answer = color.tone(scheme)
            if (
                not color.background
                or not color.background(scheme)
                or not color.contrast_curve
                or not color.contrast_curve(scheme)
            ):
                return answer

            bg_tone = color.background(scheme).get_tone(scheme)
            desired_ratio = color.contrast_curve(scheme).get(scheme.contrast_level)

            if Contrast.ratio_of_tones(bg_tone, answer) >= desired_ratio:
                pass
            else:
                answer = DynamicColor.foreground_tone(bg_tone, desired_ratio)

            if decreasing_contrast:
                answer = DynamicColor.foreground_tone(bg_tone, desired_ratio)

            if color.is_background and 50 <= answer < 60:
                if Contrast.ratio_of_tones(49, bg_tone) >= desired_ratio:
                    answer = 49
                else:
                    answer = 60

            if not color.second_background or not color.second_background(scheme):
                return answer

            bg1 = color.background(scheme)
            bg2 = color.second_background(scheme)
            bg_tone1 = bg1.get_tone(scheme)
            bg_tone2 = bg2.get_tone(scheme)
            upper = max(bg_tone1, bg_tone2)
            lower = min(bg_tone1, bg_tone2)

            if (
                Contrast.ratio_of_tones(upper, answer) >= desired_ratio
                and Contrast.ratio_of_tones(lower, answer) >= desired_ratio
            ):
                return answer

            light_option = Contrast.lighter(upper, desired_ratio)
            dark_option = Contrast.darker(lower, desired_ratio)

            availables = []
            if light_option != -1:
                availables.append(light_option)
            if dark_option != -1:
                availables.append(dark_option)

            prefers_light = DynamicColor.tone_prefers_light_foreground(
                bg_tone1
            ) or DynamicColor.tone_prefers_light_foreground(bg_tone2)
            if prefers_light:
                return 100 if light_option < 0 else light_option
            if len(availables) == 1:
                return availables[0]
            return 0 if dark_option < 0 else dark_option


class ColorCalculationDelegateImpl2025(ColorCalculationDelegate):
    @staticmethod
    def _is_fixed_dim_name(name: str) -> bool:
        lowered = name.lower()
        return lowered.endswith("_fixed_dim") or lowered.endswith("fixeddim")

    def get_hct(self, scheme: "DynamicScheme", color: "DynamicColor") -> "Hct":
        palette = color.palette(scheme)
        tone = color.get_tone(scheme)
        hue = palette.hue
        chroma = palette.chroma * (
            color.chroma_multiplier(scheme) if color.chroma_multiplier else 1
        )
        return Hct.from_hct(hue, chroma, tone)

    def get_tone(self, scheme: "DynamicScheme", color: "DynamicColor") -> float:
        from materialyoucolor.dynamiccolor.dynamic_color import DynamicColor

        tone_delta_pair = (
            color.tone_delta_pair(scheme) if color.tone_delta_pair else None
        )

        if tone_delta_pair:
            role_a = tone_delta_pair.role_a
            role_b = tone_delta_pair.role_b
            polarity = tone_delta_pair.polarity
            constraint = tone_delta_pair.constraint
            absolute_delta = (
                -tone_delta_pair.delta
                if polarity == "darker"
                or (polarity == "relative_lighter" and scheme.is_dark)
                or (polarity == "relative_darker" and not scheme.is_dark)
                else tone_delta_pair.delta
            )

            am_role_a = color.name == role_a.name
            self_role = role_a if am_role_a else role_b
            ref_role = role_b if am_role_a else role_a
            self_tone = self_role.tone(scheme)
            ref_tone = ref_role.get_tone(scheme)
            relative_delta = absolute_delta * (1 if am_role_a else -1)

            if constraint == "exact":
                self_tone = clamp_double(0, 100, ref_tone + relative_delta)
            elif constraint == "nearer":
                if relative_delta > 0:
                    self_tone = clamp_double(
                        0,
                        100,
                        clamp_double(ref_tone, ref_tone + relative_delta, self_tone),
                    )
                else:
                    self_tone = clamp_double(
                        0,
                        100,
                        clamp_double(ref_tone + relative_delta, ref_tone, self_tone),
                    )
            elif constraint == "farther":
                if relative_delta > 0:
                    self_tone = clamp_double(ref_tone + relative_delta, 100, self_tone)
                else:
                    self_tone = clamp_double(0, ref_tone + relative_delta, self_tone)

            if color.background and color.contrast_curve:
                background = color.background(scheme)
                contrast_curve = color.contrast_curve(scheme)
                if background and contrast_curve:
                    bg_tone = background.get_tone(scheme)
                    self_contrast = contrast_curve.get(scheme.contrast_level)
                    self_tone = (
                        self_tone
                        if Contrast.ratio_of_tones(bg_tone, self_tone) >= self_contrast
                        and scheme.contrast_level >= 0
                        else DynamicColor.foreground_tone(bg_tone, self_contrast)
                    )

            if color.is_background and not self._is_fixed_dim_name(color.name):
                if self_tone >= 57:
                    self_tone = clamp_double(65, 100, self_tone)
                else:
                    self_tone = clamp_double(0, 49, self_tone)
            return self_tone
        else:
            answer = color.tone(scheme)
            if (
                not color.background
                or not color.background(scheme)
                or not color.contrast_curve
                or not color.contrast_curve(scheme)
            ):
                return answer

            bg_tone = color.background(scheme).get_tone(scheme)
            desired_ratio = color.contrast_curve(scheme).get(scheme.contrast_level)

            answer = (
                answer
                if Contrast.ratio_of_tones(bg_tone, answer) >= desired_ratio
                and scheme.contrast_level >= 0
                else DynamicColor.foreground_tone(bg_tone, desired_ratio)
            )

            if color.is_background and not self._is_fixed_dim_name(color.name):
                if answer >= 57:
                    answer = clamp_double(65, 100, answer)
                else:
                    answer = clamp_double(0, 49, answer)

            if not color.second_background or not color.second_background(scheme):
                return answer

            bg1 = color.background(scheme)
            bg2 = color.second_background(scheme)
            bg_tone1 = bg1.get_tone(scheme)
            bg_tone2 = bg2.get_tone(scheme)
            upper = max(bg_tone1, bg_tone2)
            lower = min(bg_tone1, bg_tone2)

            if (
                Contrast.ratio_of_tones(upper, answer) >= desired_ratio
                and Contrast.ratio_of_tones(lower, answer) >= desired_ratio
            ):
                return answer

            light_option = Contrast.lighter(upper, desired_ratio)
            dark_option = Contrast.darker(lower, desired_ratio)

            availables = []
            if light_option != -1:
                availables.append(light_option)
            if dark_option != -1:
                availables.append(dark_option)

            prefers_light = DynamicColor.tone_prefers_light_foreground(
                bg_tone1
            ) or DynamicColor.tone_prefers_light_foreground(bg_tone2)
            if prefers_light:
                return 100 if light_option < 0 else light_option
            if len(availables) == 1:
                return availables[0]
            return 0 if dark_option < 0 else dark_option


_spec2021_calc = ColorCalculationDelegateImpl2021()
_spec2025_calc = ColorCalculationDelegateImpl2025()


def get_color_calculation_delegate(
    spec_version: "SpecVersion",
) -> ColorCalculationDelegate:
    return _spec2025_calc if spec_version == "2025" else _spec2021_calc
