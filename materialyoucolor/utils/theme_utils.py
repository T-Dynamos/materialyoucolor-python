from typing import Any, Dict, List, Optional

from materialyoucolor.blend.blend import Blend
from materialyoucolor.palettes.core_palette import CorePalette
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.scheme.scheme import Scheme
from materialyoucolor.utils.image_utils import source_color_from_image_bytes
from materialyoucolor.utils.string_utils import hex_from_argb


class CustomColor:
    def __init__(self, value: int, name: str, blend: bool):
        self.value = value
        self.name = name
        self.blend = blend


class ColorGroup:
    def __init__(
        self, color: int, on_color: int, color_container: int, on_color_container: int
    ):
        self.color = color
        self.on_color = on_color
        self.color_container = color_container
        self.on_color_container = on_color_container


class CustomColorGroup:
    def __init__(
        self, color: CustomColor, value: int, light: ColorGroup, dark: ColorGroup
    ):
        self.color = color
        self.value = value
        self.light = light
        self.dark = dark


class Theme:
    def __init__(
        self,
        source: int,
        schemes: Dict[str, Scheme],
        palettes: Dict[str, TonalPalette],
        custom_colors: List[CustomColorGroup],
    ):
        self.source = source
        self.schemes = schemes
        self.palettes = palettes
        self.custom_colors = custom_colors


def theme_from_source_color(
    source: int, custom_colors: Optional[List[CustomColor]] = None
) -> Theme:
    if custom_colors is None:
        custom_colors = []
    palette = CorePalette.of(source)
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
        [custom_color_group(source, c) for c in custom_colors],
    )


def custom_color_group(source: int, custom_color: CustomColor) -> CustomColorGroup:
    value = custom_color.value
    if custom_color.blend:
        value = Blend.harmonize(custom_color.value, source)
    palette = CorePalette.of(value)
    tones = palette.a1
    return CustomColorGroup(
        custom_color,
        value,
        ColorGroup(tones.tone(40), tones.tone(100), tones.tone(90), tones.tone(10)),
        ColorGroup(tones.tone(80), tones.tone(20), tones.tone(30), tones.tone(90)),
    )
