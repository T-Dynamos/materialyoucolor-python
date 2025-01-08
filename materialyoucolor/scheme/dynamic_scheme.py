from materialyoucolor.hct import Hct
from materialyoucolor.palettes.tonal_palette import TonalPalette
from materialyoucolor.scheme.variant import Variant
from materialyoucolor.utils.math_utils import sanitize_degrees_double


class DynamicSchemeOptions:
    def __init__(
        self,
        source_color_hct: Hct,
        variant: Variant,
        contrast_level: int,
        is_dark: bool,
        primary_palette: TonalPalette,
        secondary_palette: TonalPalette,
        tertiary_palette: TonalPalette,
        neutral_palette: TonalPalette,
        neutral_variant_palette: TonalPalette,
        error_palette: TonalPalette = None,
    ):
        self.source_color_argb = source_color_hct.to_int()
        self.source_color_hct = source_color_hct
        self.variant = variant
        self.contrast_level = contrast_level
        self.is_dark = is_dark
        self.primary_palette = primary_palette
        self.secondary_palette = secondary_palette
        self.tertiary_palette = tertiary_palette
        self.neutral_palette = neutral_palette
        self.neutral_variant_palette = neutral_variant_palette
        self.error_palette = error_palette


class DynamicScheme:
    def __init__(self, args: DynamicSchemeOptions):
        self.source_color_argb = args.source_color_argb
        self.variant = args.variant
        self.contrast_level = args.contrast_level
        self.is_dark = args.is_dark
        self.source_color_hct = args.source_color_hct
        self.primary_palette = args.primary_palette
        self.secondary_palette = args.secondary_palette
        self.tertiary_palette = args.tertiary_palette
        self.neutral_palette = args.neutral_palette
        self.neutral_variant_palette = args.neutral_variant_palette
        if args.error_palette is None:
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
