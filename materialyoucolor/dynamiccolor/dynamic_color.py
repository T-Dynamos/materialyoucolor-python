from materialyoucolor.contrast import Contrast
from materialyoucolor.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.scheme.dynamic_scheme import DynamicScheme
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve
from materialyoucolor.dynamiccolor.tone_delta_pair import ToneDeltaPair
from materialyoucolor.utils.math_utils import clamp_double

from dataclasses import dataclass


@dataclass
class FromPaletteOptions:
    name: str = ""
    palette: TonalPalette = None
    tone: float = None
    is_background: bool = None
    background: object = None
    second_background: object = None
    contrast_curve: ContrastCurve = None
    tone_delta_pair: ToneDeltaPair = None
    chroma_multiplier : float = None


@dataclass
class DynamicColor(FromPaletteOptions):

    hct_cache = {}
    def __post_init__(self):
        self.hct_cache = {}
        if not self.background and self.second_background:
            raise ValueError(
                f"Color {name} has secondBackground defined, but background is not defined."
            )
        if not self.background and self.contrast_curve:
            raise ValueError(
                f"Color {name} has contrastCurve defined, but background is not defined."
            )
        if self.background and not self.contrast_curve:
            raise ValueError(
                f"Color {name} has background defined, but contrastCurve is not defined."
            )

    @staticmethod
    def from_palette(args: FromPaletteOptions):
        return DynamicColor(**vars(args)) 

    def get_argb(self, scheme: DynamicScheme) -> int:
        return self.get_hct(scheme).to_int()

    def get_hct(self, scheme: DynamicScheme) -> Hct:
        cached_answer = self.hct_cache.get(scheme)
        if cached_answer is not None:
            return cached_answer

        tone = self.get_tone(scheme)
        answer = self.palette(scheme).get_hct(tone)
        if len(self.hct_cache) > 4:
            self.hct_cache.clear()
        self.hct_cache[scheme] = answer
        return answer

    def get_tone(self, scheme):
        tone_delta_pair = self.tone_delta_pair(scheme) if self.tone_delta_pair else None
        print(self.name)
        # Case 0: tone delta constraint
        if tone_delta_pair:
            role_a = tone_delta_pair.role_a
            role_b = tone_delta_pair.role_b
            polarity = tone_delta_pair.polarity
            constraint = tone_delta_pair.constraint
            delta = tone_delta_pair.delta

            # Determine direction of tone shift
            if polarity in ("darker",) or (polarity == "relative_lighter" and scheme.is_dark) or (
                polarity == "relative_darker" and not scheme.is_dark
            ):
                absolute_delta = -delta
            else:
                absolute_delta = delta

            am_role_a = self.name == role_a.name
            self_role = role_a if am_role_a else role_b
            ref_role = role_b if am_role_a else role_a

            self_tone = self_role.tone(scheme)
            ref_tone = ref_role.get_tone(scheme)
            relative_delta = absolute_delta * (1 if am_role_a else -1)

            # Handle constraints
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

            # Adjust for contrast curve if applicable
            if self.background and self.contrast_curve:
                background = self.background(scheme)
                contrast_curve = self.contrast_curve(scheme)
                if background and contrast_curve:
                    bg_tone = background.get_tone(scheme)
                    self_contrast = contrast_curve.get(scheme.contrast_level)
                    if Contrast.ratio_of_tones(bg_tone, self_tone) < self_contrast or scheme.contrast_level < 0:
                        self_tone = DynamicColor.foreground_tone(bg_tone, self_contrast)

            # Avoid awkward tones for background colors
            if self.is_background and not self.name.endswith("_fixed_dim"):
                if self_tone >= 57:
                    self_tone = clamp_double(65, 100, self_tone)
                else:
                    self_tone = clamp_double(0, 49, self_tone)

            return self_tone

        # Case 1: no tone delta pair; solve self
        answer = self.tone(scheme)

        if (
            not self.background
            or not self.contrast_curve
        ):
            return answer

        bg_tone = self.background(scheme).get_tone(scheme)
        desired_ratio = self.contrast_curve.get(scheme.contrast_level)

        if Contrast.ratio_of_tones(bg_tone, answer) < desired_ratio or scheme.contrast_level < 0:
            answer = DynamicColor.foreground_tone(bg_tone, desired_ratio)

        if self.is_background and not self.name.endswith("_fixed_dim"):
            if answer >= 57:
                answer = clamp_double(65, 100, answer)
            else:
                answer = clamp_double(0, 49, answer)

        if not self.second_background or not self.second_background(scheme):
            return answer

        # Case 2: dual backgrounds
        bg1 = self.background
        bg2 = self.second_background
        bg_tone1 = bg1(scheme).get_tone(scheme)
        bg_tone2 = bg2(scheme).get_tone(scheme)
        upper, lower = max(bg_tone1, bg_tone2), min(bg_tone1, bg_tone2)

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

        prefers_light = DynamicColor.tone_prefers_light_foreground(bg_tone1) or DynamicColor.tone_prefers_light_foreground(bg_tone2)
        if prefers_light:
            return 100 if light_option < 0 else light_option
        if len(availables) == 1:
            return availables[0]
        return 0 if dark_option < 0 else dark_option


    @staticmethod
    def foreground_tone(bg_tone, ratio):
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
    def tone_prefers_light_foreground(tone):
        return round(tone) < 60.0

    @staticmethod
    def tone_allows_light_foreground(tone):
        return round(tone) <= 49.0

    @staticmethod
    def enable_light_foreground(tone):
        if DynamicColor.tone_prefers_light_foreground(
            tone
        ) and not DynamicColor.tone_allows_light_foreground(tone):
            return 49.0
        return tone
