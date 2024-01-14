from materialyoucolor.blend import Blend
from materialyoucolor.palettes.core_palette import CorePalette
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.scheme import Scheme
from materialyoucolor.utils.image_utils import source_color_from_image
from materialyoucolor.dislike.dislike_analyzer import DislikeAnalyzer
from materialyoucolor.hct import Hct


class Theme:
    def __init__(
        self,
        source: int,
        schemes: dict,
        palettes: dict,
        custom_colors: list[dict],
    ):
        self.source = source
        self.schemes = schemes
        self.palettes = palettes
        self.custom_colors = custom_colors


def custom_color(custom_color, source_color=None, blend=False):
    value = DislikeAnalyzer.fix_if_disliked(Hct.from_int(custom_color))
    if blend:
        value = Blend.harmonize(value, source_color)
    palette = CorePalette.of(value)
    tones = palette.a1
    return {
        "color": custom_color,
        "theme_color": source_color,
        "blended": blend,
        "light": {
            "color": tones.tone(40),
            "onColor": tones.tone(100),
            "colorContainer": tones.tone(90),
            "onColorContainer": tones.tone(10),
        },
        "dark": {
            "color": tones.tone(80),
            "onColor": tones.tone(20),
            "colorContainer": tones.tone(30),
            "onColorContainer": tones.tone(90),
        },
    }


def theme_from_source_color(
    source: int, custom_colors=[], fix_if_disliked=False
) -> Theme:
    palette = CorePalette.of(
        DislikeAnalyzer.fix_if_disliked(Hct.from_int(source)).to_int()
        if fix_if_disliked
        else source
    )
    return Theme(
        source,
        {"light": Scheme.light(source), "dark": Scheme.dark(source)},
        {
            "primary": palette.a1,
            "secondary": palette.a2,
            "tertiary": palette.a3,
            "neutral": palette.n1,
            "neutralVariant": palette.n2,
            "error": palette.error,
        },
        [
            custom_color(color, blend=True, source_color=source)
            for color in custom_colors
        ],
    )
