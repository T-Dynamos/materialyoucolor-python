from materialyoucolor.dislike.dislike_analyzer import DislikeAnalyzer
from materialyoucolor.hct import Hct
from materialyoucolor.scheme.dynamic_scheme import DynamicScheme
from materialyoucolor.scheme.variant import Variant
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve
from materialyoucolor.dynamiccolor.tone_delta_pair import ToneDeltaPair
from materialyoucolor.dynamiccolor.dynamic_color import FromPaletteOptions, DynamicColor


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


class MaterialDynamicColors:
    content_accent_tone_delta = 15.0

    # TODO: implement it
