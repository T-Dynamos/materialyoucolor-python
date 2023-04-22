from materialyoucolor.blend.blend import Blend
from materialyoucolor.palettes.core_palette import CorePalette
from materialyoucolor.scheme.scheme import Scheme
from materialyoucolor.utils.color_utils import DominantColor
import os
from materialyoucolor.score import score
from materialyoucolor.hct import hct 

def tempConvert(rgb):
    r, g, b = rgb
    return 0xFF000000 | (r << 16) | (g << 8) | b

# dislike algorithm
def materialize(color):
    hct_ = hct.Hct.fromInt(color)
    huePasses = all([round(hct_.hue) >= 90.0, round(hct_.hue) <= 111.0])
    chromaPasses = round(hct_.chroma) > 16.0
    tonePasses = round(hct_.tone) < 65.0
    if all([huePasses, chromaPasses, tonePasses]) == False:
        return hct.Hct.fromHct(
            hct_.hue,
            hct_.chroma,
            70.0,
        ).toInt()
    else:
        return color

def temp(colors):
    argb_count = {}
    for color in colors:
        r, g, b = color
        a = 255
        argb = (a << 24) + (r << 16) + (g << 8) + b
        # No option to just fix it to ten and make proportions equal
        # then this will prioritize chroma when proportions are equal
        argb_count[argb] = argb_count.get(argb, 0) + 10 
    return argb_count


def getDominantColors(image, quality=None, default_chunk = 128):
    color_ = DominantColor(image)
    colors = color_.get_palette(
        color_count=default_chunk,
        quality=(round(os.path.getsize(image) / 10000 if quality is None else quality)),
    )
    score_final = score.Score(temp(colors))
    return [materialize(co) for co in score_final]


def customColor(custom_color, source_color=None, blend=False):
    value = materialize(custom_color)
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


def getDefaultTheme():
    return Scheme.default()


def themeFromSourceColor(source, customColors=[]):
    palette = CorePalette.of(source)
    return {
        "source": source,
        "schemes": {
            "light": Scheme.light(source),
            "dark": Scheme.dark(source),
        },
        "palettes": {
            "primary": palette.a1,
            "secondary": palette.a2,
            "tertiary": palette.a3,
            "neutral": palette.n1,
            "neutralVariant": palette.n2,
            "error": palette.error,
        },
        "customColors": [customColor(c, blend=True, source_color=source) for c in customColors],
    }


def themeFromImage(image, customColors=[]):
    source = sourceColorFromImage(image)
    return themeFromSourceColor(source, customColors)
