from materialyoucolor.palettes.core_palette import CorePalette
from materialyoucolor.utils.color_utils import argb_from_rgba


class SchemeAndroid:
    def __init__(self, props: dict):
        self.props = props
        [setattr(self, _, self.props[_]) for _ in self.props.keys()]

    @staticmethod
    def light_from_rgb(rgb: list[int]):
        return SchemeAndroid.light_from_core_palette(
            CorePalette.of(argb_from_rgba(rgb))
        )

    @staticmethod
    def light(argb: int):
        return SchemeAndroid.light_from_core_palette(CorePalette.of(argb))

    @staticmethod
    def light_content(argb: int):
        return SchemeAndroid.light_from_core_palette(CorePalette.content_of(argb))

    @staticmethod
    def light_from_core_palette(core: CorePalette):
        return SchemeAndroid(
            {
                "colorAccentPrimary": core.a1.tone(90),
                "colorAccentPrimaryVariant": core.a1.tone(40),
                "colorAccentSecondary": core.a2.tone(90),
                "colorAccentSecondaryVariant": core.a2.tone(40),
                "colorAccentTertiary": core.a3.tone(90),
                "colorAccentTertiaryVariant": core.a3.tone(40),
                "textColorPrimary": core.n1.tone(10),
                "textColorSecondary": core.n2.tone(30),
                "textColorTertiary": core.n2.tone(50),
                "textColorPrimaryInverse": core.n1.tone(95),
                "textColorSecondaryInverse": core.n1.tone(80),
                "textColorTertiaryInverse": core.n1.tone(60),
                "colorBackground": core.n1.tone(95),
                "colorBackgroundFloating": core.n1.tone(98),
                "colorSurface": core.n1.tone(98),
                "colorSurfaceVariant": core.n1.tone(90),
                "colorSurfaceHighlight": core.n1.tone(100),
                "surfaceHeader": core.n1.tone(90),
                "underSurface": core.n1.tone(0),
                "offState": core.n1.tone(20),
                "accentSurface": core.a2.tone(95),
                "textPrimaryOnAccent": core.n1.tone(10),
                "textSecondaryOnAccent": core.n2.tone(30),
                "volumeBackground": core.n1.tone(25),
                "scrim": core.n1.tone(80),
            }
        )

    @staticmethod
    def dark_from_rgb(rgb: list[int]):
        return SchemeAndroid.dark_from_core_palette(CorePalette.of(argb_from_rgba(rgb)))

    @staticmethod
    def dark(argb: int):
        return SchemeAndroid.dark_from_core_palette(CorePalette.of(argb))

    @staticmethod
    def dark_content(argb: int):
        return SchemeAndroid.dark_from_core_palette(CorePalette.content_of(argb))

    @staticmethod
    def dark_from_core_palette(core: CorePalette):
        return SchemeAndroid(
            {
                "colorAccentPrimary": core.a1.tone(90),
                "colorAccentPrimaryVariant": core.a1.tone(70),
                "colorAccentSecondary": core.a2.tone(90),
                "colorAccentSecondaryVariant": core.a2.tone(70),
                "colorAccentTertiary": core.a3.tone(90),
                "colorAccentTertiaryVariant": core.a3.tone(70),
                "textColorPrimary": core.n1.tone(95),
                "textColorSecondary": core.n2.tone(80),
                "textColorTertiary": core.n2.tone(60),
                "textColorPrimaryInverse": core.n1.tone(10),
                "textColorSecondaryInverse": core.n1.tone(30),
                "textColorTertiaryInverse": core.n1.tone(50),
                "colorBackground": core.n1.tone(10),
                "colorBackgroundFloating": core.n1.tone(10),
                "colorSurface": core.n1.tone(20),
                "colorSurfaceVariant": core.n1.tone(30),
                "colorSurfaceHighlight": core.n1.tone(35),
                "surfaceHeader": core.n1.tone(30),
                "underSurface": core.n1.tone(0),
                "offState": core.n1.tone(20),
                "accentSurface": core.a2.tone(95),
                "textPrimaryOnAccent": core.n1.tone(10),
                "textSecondaryOnAccent": core.n2.tone(30),
                "volumeBackground": core.n1.tone(25),
                "scrim": core.n1.tone(80),
            }
        )
