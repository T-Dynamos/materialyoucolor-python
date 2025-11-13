from materialyoucolor.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.scheme.variant import Variant
from materialyoucolor.utils.math_utils import sanitize_degrees_double
from dataclasses import dataclass

@dataclass
class DynamicSchemeOptions:
    source_color_hct: Hct
    variant: Variant
    contrast_level: int
    is_dark: bool
    primary_palette: TonalPalette
    secondary_palette: TonalPalette
    tertiary_palette: TonalPalette
    neutral_palette: TonalPalette
    neutral_variant_palette: TonalPalette
    error_palette: TonalPalette = None
    platform: str = "phone"

    def __post_init__(self):
        self.source_color_argb = self.source_color_hct.to_int()


class DynamicScheme:
    def __init__(self, scheme_options: DynamicSchemeOptions):
        self.__dict__.update(vars(scheme_options))

        if self.error_palette is None:
            self.error_palette = TonalPalette.from_hue_and_chroma(25.0, 84.0)

    @staticmethod
    def get_rotated_hue(source_color, hues, rotations):
        source_hue = source_color.hue
        if len(hues) != len(rotations):
            raise ValueError(
                f"mismatch between hue length {len(hues)} & rotations {len(rotations)}"
            )
        if len(rotations) == 1:
            return sanitize_degrees_double(source_color.hue + rotations[0])
        size = len(hues)
        for i in range(size - 1):
            this_hue = hues[i]
            next_hue = hues[i + 1]
            if this_hue < source_hue < next_hue:
                return sanitize_degrees_double(source_hue + rotations[i])
        return source_hue
