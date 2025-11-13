from typing import Any, Dict, List, Optional

from materialyoucolor.hct.hct import Hct
from materialyoucolor.utils.math_utils import difference_degrees, sanitize_degrees_int


class ScoreOptions:
    def __init__(
        self,
        desired: int = 4,
        fallback_color_argb: int = 0xFF4285F4,
        filter: bool = True,
    ):
        self.desired = desired
        self.fallback_color_argb = fallback_color_argb
        self.filter = filter


SCORE_OPTION_DEFAULTS = ScoreOptions()


def compare(a: Dict[str, Any], b: Dict[str, Any]) -> int:
    if a["score"] > b["score"]:
        return -1
    elif a["score"] < b["score"]:
        return 1
    return 0


class Score:
    TARGET_CHROMA = 48.0
    WEIGHT_PROPORTION = 0.7
    WEIGHT_CHROMA_ABOVE = 0.3
    WEIGHT_CHROMA_BELOW = 0.1
    CUTOFF_CHROMA = 5.0
    CUTOFF_EXCITED_PROPORTION = 0.01

    def __init__(self):
        pass

    @staticmethod
    def score(
        colors_to_population: Dict[int, int], options: Optional[ScoreOptions] = None
    ) -> List[int]:
        if options is None:
            options = SCORE_OPTION_DEFAULTS

        desired = options.desired
        fallback_color_argb = options.fallback_color_argb
        filter_enabled = options.filter

        colors_hct: List[Hct] = []
        hue_population = [0] * 360
        population_sum = 0

        for argb, population in colors_to_population.items():
            hct = Hct.from_int(argb)
            colors_hct.append(hct)
            hue = int(hct.hue)
            hue_population[hue] += population
            population_sum += population

        hue_excited_proportions = [0.0] * 360

        for hue in range(360):
            proportion = hue_population[hue] / population_sum
            for i in range(hue - 14, hue + 16):
                neighbor_hue = sanitize_degrees_int(i)
                hue_excited_proportions[neighbor_hue] += proportion

        scored_hct: List[Dict[str, Any]] = []
        for hct in colors_hct:
            hue = sanitize_degrees_int(round(hct.hue))
            proportion = hue_excited_proportions[hue]

            if filter_enabled and (
                hct.chroma < Score.CUTOFF_CHROMA
                or proportion <= Score.CUTOFF_EXCITED_PROPORTION
            ):
                continue

            proportion_score = proportion * 100.0 * Score.WEIGHT_PROPORTION
            chroma_weight = (
                Score.WEIGHT_CHROMA_BELOW
                if hct.chroma < Score.TARGET_CHROMA
                else Score.WEIGHT_CHROMA_ABOVE
            )
            chroma_score = (hct.chroma - Score.TARGET_CHROMA) * chroma_weight
            score_value = proportion_score + chroma_score
            scored_hct.append({"hct": hct, "score": score_value})

        scored_hct.sort(key=lambda x: x["score"], reverse=True)

        chosen_colors: List[Hct] = []
        for difference_degrees_ in range(90, 14, -1):
            chosen_colors.clear()
            for item in scored_hct:
                hct = item["hct"]
                duplicate_hue = any(
                    difference_degrees(hct.hue, chosen_hct.hue) < difference_degrees_
                    for chosen_hct in chosen_colors
                )
                if not duplicate_hue:
                    chosen_colors.append(hct)
                if len(chosen_colors) >= desired:
                    break
            if len(chosen_colors) >= desired:
                break

        colors: List[int] = []
        if not chosen_colors:
            colors.append(fallback_color_argb)
        else:
            for chosen_hct in chosen_colors:
                colors.append(chosen_hct.to_int())
        return colors
