from blend.blend import Blend
from palettes.core_palette import CorePalette
from scheme.scheme import Scheme

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