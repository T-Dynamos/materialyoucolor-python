from materialyoucolor.hct.cam16 import Cam16
from materialyoucolor.utils.color_utils import lstarFromArgb
from materialyoucolor.utils.math_utils import sanitizeDegreesInt, differenceDegrees
from typing import List, Tuple, Dict
from collections import defaultdict
import math

TARGET_CHROMA = 48.0
WEIGHT_PROPORTION = 0.7
WEIGHT_CHROMA_ABOVE = 0.3
WEIGHT_CHROMA_BELOW = 0.1
CUTOFF_CHROMA = 15.0
CUTOFF_TONE = 10.0
CUTOFF_EXCITED_PROPORTION = 0.01


def filter_excited(
    colorsToExcitedProportion: Dict[int, float], colorsToCam: Dict[int, Cam16]
) -> List[int]:
    filtered = []
    for color, cam in colorsToCam.items():
        proportion = colorsToExcitedProportion.get(color, 0.0)
        if (
            cam.chroma >= CUTOFF_CHROMA
            and lstarFromArgb(color) >= CUTOFF_TONE
            and proportion >= CUTOFF_EXCITED_PROPORTION
        ):
            filtered.append(color)
    return filtered


def filter_content(colorsToCam: Dict[int, Cam16]) -> List[int]:
    return list(colorsToCam.keys())


def Score(
    colors_to_population: Dict[int, int], content_color: bool = False
) -> List[int]:

    population_sum = sum(colors_to_population.values())
    colors_to_proportion = {}
    colors_to_cam = {}
    hue_proportions = defaultdict(int)

    for color, population in colors_to_population.items():
        proportion = population / population_sum
        colors_to_proportion[color] = proportion
        cam = Cam16.fromInt(color)
        colors_to_cam[color] = cam
        hue = round(cam.hue)
        hue_proportions[hue] += proportion

    colors_to_excited_proportion = {}
    for color, cam in colors_to_cam.items():
        hue = round(cam.hue)

        excited_proportion = 0
        for i in range(hue - 15, hue + 15):
            neighbor_hue = sanitizeDegreesInt(i)
            excited_proportion += hue_proportions[neighbor_hue]

        colors_to_excited_proportion[color] = excited_proportion

    colors_to_score = {}
    for color, cam in colors_to_cam.items():
        proportion = colors_to_excited_proportion[color]
        proportion_score = proportion * 100.0 * WEIGHT_PROPORTION

        chroma_weight = (
            WEIGHT_CHROMA_BELOW if cam.chroma < TARGET_CHROMA else WEIGHT_CHROMA_ABOVE
        )
        chroma_score = (cam.chroma - TARGET_CHROMA) * chroma_weight

        score = proportion_score + chroma_score
        colors_to_score[color] = score

    filtered_colors = (
        filter_content(colors_to_cam)
        if content_color
        else filter_excited(colors_to_excited_proportion, colors_to_cam)
    )
    deduped_colors_to_score = {}

    for color in filtered_colors:
        duplicate_hue = False
        hue = colors_to_cam[color].hue
        for already_chosen_color in deduped_colors_to_score.keys():
            already_chosen_hue = colors_to_cam[already_chosen_color].hue
            if differenceDegrees(hue, already_chosen_hue) < 15:
                duplicate_hue = True
                break

        if not duplicate_hue:
            deduped_colors_to_score[color] = colors_to_score[color]

    colors_by_score_descending = sorted(
        deduped_colors_to_score.items(), key=lambda x: x[1], reverse=True
    )
    answer = [entry[0] for entry in colors_by_score_descending]

    if not answer:
        answer.append(0xFF4285F4)  # Google Blue

    return answer
