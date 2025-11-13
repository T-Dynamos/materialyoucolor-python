from typing import List

from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score


def source_color_from_image_bytes(image_data: List[int], pixel_len=None) -> int:
    if pixel_len is None:
        pixel_len = len(image_data)
    result = QuantizeCelebi([image_data[i] for i in range(0, pixel_len)], 128)
    ranked = Score.score(result)
    top = ranked[0]
    return top
