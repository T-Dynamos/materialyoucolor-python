from materialyoucolor.contrast import Contrast
from materialyoucolor.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.scheme.dynamic_scheme import DynamicScheme
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve
from materialyoucolor.dynamiccolor.tone_delta_pair import ToneDeltaPair


class FromPaletteOptions:
    def __init__(
        self,
        name=str,
        palette=None,
        tone=int,
        is_background=bool,
        background=None,
        second_background=None,
        contrast_curve=None,
        tone_delta_pair=None,
    ):
        self.name = name
        self.palette = palette
        self.tone = tone
        self.is_background = is_background
        self.background = background
        self.second_background = second_background
        self.contrast_curve = contrast_curve
        self.tone_delta_pair = tone_delta_pair


class DynamicColor:
    hct_cache = dict[DynamicScheme, Hct]
    name = str
    palette = None
    tone = int
    is_background = bool
    background = None
    second_background = None
    contrast_curve = None
    tone_delta_pair = None

    def __init__(
        self,
        name=str,
        palette=None,
        tone=int,
        is_background=bool,
        background=None,
        second_background=None,
        contrast_curve=None,
        tone_delta_pair=None,
    ):
        self.name = name
        self.palette = palette
        self.tone = tone
        self.is_background = is_background
        self.background = background
        self.second_background = second_background
        self.contrast_curve = contrast_curve
        self.tone_delta_pair = tone_delta_pair
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
        return DynamicColor(
            args.name,
            args.palette,
            args.tone,
            args.is_background,
            args.background,
            args.second_background,
            args.contrast_curve,
            args.tone_delta_pair,
        )

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
        decreasing_contrast = scheme.contrast_level < 0

        if self.tone_delta_pair:
            tone_delta_pair = self.tone_delta_pair(scheme)
            role_a, role_b = tone_delta_pair.role_a, tone_delta_pair.role_b
            delta, polarity, stay_together = (
                tone_delta_pair.delta,
                tone_delta_pair.polarity,
                tone_delta_pair.stay_together,
            )

            bg = self.background(scheme)
            bg_tone = bg.get_tone(scheme)

            a_is_nearer = (
                polarity == "nearer"
                or (polarity == "lighter" and not scheme.is_dark)
                or (polarity == "darker" and scheme.is_dark)
            )
            nearer, farther = (role_a, role_b) if a_is_nearer else (role_b, role_a)
            am_nearer = self.name == nearer.name
            expansion_dir = 1 if scheme.is_dark else -1

            n_contrast = nearer.contrast_curve.get(scheme.contrast_level)
            f_contrast = farther.contrast_curve.get(scheme.contrast_level)

            n_initial_tone = nearer.tone(scheme)
            n_tone = (
                n_initial_tone
                if Contrast.ratio_of_tones(bg_tone, n_initial_tone) >= n_contrast
                else DynamicColor.foreground_tone(bg_tone, n_contrast)
            )

            f_initial_tone = farther.tone(scheme)
            f_tone = (
                f_initial_tone
                if Contrast.ratio_of_tones(bg_tone, f_initial_tone) >= f_contrast
                else DynamicColor.foreground_tone(bg_tone, f_contrast)
            )

            if decreasing_contrast:
                n_tone = DynamicColor.foreground_tone(bg_tone, n_contrast)
                f_tone = DynamicColor.foreground_tone(bg_tone, f_contrast)

            if (f_tone - n_tone) * expansion_dir >= delta:
                pass
            else:
                f_tone = (
                    min(max(n_tone + delta * expansion_dir, 0), 100)
                    if (f_tone - n_tone) * expansion_dir >= delta
                    else min(max(f_tone - delta * expansion_dir, 0), 100)
                )

            if 50 <= n_tone < 60:
                if expansion_dir > 0:
                    n_tone, f_tone = 60, max(f_tone, n_tone + delta * expansion_dir)
                else:
                    n_tone, f_tone = 49, min(f_tone, n_tone + delta * expansion_dir)
            elif 50 <= f_tone < 60:
                if stay_together:
                    if expansion_dir > 0:
                        n_tone, f_tone = 60, max(f_tone, n_tone + delta * expansion_dir)
                    else:
                        n_tone, f_tone = 49, min(f_tone, n_tone + delta * expansion_dir)
                else:
                    if expansion_dir > 0:
                        f_tone = 60
                    else:
                        f_tone = 49

            return n_tone if am_nearer else f_tone

        else:
            answer = self.tone(scheme)

            if self.background is None:
                return answer

            bg_tone = self.background(scheme).get_tone(scheme)
            desired_ratio = self.contrast_curve.get(scheme.contrast_level)

            if Contrast.ratio_of_tones(bg_tone, answer) >= desired_ratio:
                pass
            else:
                answer = DynamicColor.foreground_tone(bg_tone, desired_ratio)

            if decreasing_contrast:
                answer = DynamicColor.foreground_tone(bg_tone, desired_ratio)

            if self.is_background and 50 <= answer < 60:
                answer = (
                    49 if Contrast.ratio_of_tones(49, bg_tone) >= desired_ratio else 60
                )

            if self.second_background:
                bg1, bg2 = self.background, self.second_background
                bg_tone1, bg_tone2 = bg1(scheme).get_tone(scheme), bg2(scheme).get_tone(
                    scheme
                )
                upper, lower = max(bg_tone1, bg_tone2), min(bg_tone1, bg_tone2)

                if (
                    Contrast.ratio_of_tones(upper, answer) >= desired_ratio
                    and Contrast.ratio_of_tones(lower, answer) >= desired_ratio
                ):
                    return answer

                light_option = Contrast.lighter(upper, desired_ratio)
                dark_option = Contrast.darker(lower, desired_ratio)
                availables = [light_option] if light_option != -1 else []
                if dark_option != -1:
                    availables.append(dark_option)

                prefers_light = DynamicColor.tone_prefers_light_foreground(
                    bg_tone1
                ) or DynamicColor.tone_prefers_light_foreground(bg_tone2)
                return (
                    light_option
                    if prefers_light and (light_option == -1 or dark_option == -1)
                    else dark_option
                )

            return answer

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
