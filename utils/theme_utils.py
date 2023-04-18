from blend.blend import Blend
from palettes.core_palette import CorePalette
from scheme.scheme import Scheme
from utils.color_utils import DominantColor
import os
from score import score


def tempConvert(rgb):
    r, g, b = rgb
    return 0xFF000000 | (r << 16) | (g << 8) | b


def temp(colors):
    argb_count = {}
    for color in colors:
        r, g, b = color
        a = 255
        argb = (a << 24) + (r << 16) + (g << 8) + b
        argb_count[argb] = argb_count.get(argb, 0) + 10
    return argb_count


def getDominantColors(image, quality=None, default_chunk = 50):
    color_ = DominantColor(image)
    colors = color_.get_palette(
        color_count=default_chunk,
        quality=(round(os.path.getsize(image) / 10000 if quality is None else quality)),
    )
    score_final = score.Score(temp(colors))
    return score_final


def customColor(source, color):
    value = color["value"]
    from_v = value
    to = source
    if color["blend"]:
        value = Blend.harmonize(from_v, to)
    palette = CorePalette.of(value)
    tones = palette.a1
    return {
        "color": color,
        "value": value,
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
        "customColors": [customColor(source, c) for c in customColors],
    }


def themeFromImage(image, customColors=[]):
    source = sourceColorFromImage(image)
    return themeFromSourceColor(source, customColors)
