from materialyoucolor.palettes.core_palette import CorePalette
from materialyoucolor.utils.color_utils import argb_from_rgba


class Scheme:
    def __init__(self, props: dict):
        self.props = props
        [setattr(self, _, self.props[_]) for _ in self.props.keys()]

    @staticmethod
    def light_from_rgb(rgb: list[int]):
        return Scheme.light_from_core_palette(CorePalette.of(argb_from_rgba(rgb)))

    @staticmethod
    def light(argb: int):
        return Scheme.light_from_core_palette(CorePalette.of(argb))

    @staticmethod
    def light_content(argb: int):
        return Scheme.light_from_core_palette(CorePalette.content_of(argb))

    @staticmethod
    def light_from_core_palette(core: CorePalette):
        return Scheme(
            {
                "primary": core.a1.tone(40),
                "onPrimary": core.a1.tone(100),
                "primaryContainer": core.a1.tone(90),
                "onPrimaryContainer": core.a1.tone(10),
                "secondary": core.a2.tone(40),
                "onSecondary": core.a2.tone(100),
                "secondaryContainer": core.a2.tone(90),
                "onSecondaryContainer": core.a2.tone(10),
                "tertiary": core.a3.tone(40),
                "onTertiary": core.a3.tone(100),
                "tertiaryContainer": core.a3.tone(90),
                "onTertiaryContainer": core.a3.tone(10),
                "error": core.error.tone(40),
                "onError": core.error.tone(100),
                "errorContainer": core.error.tone(90),
                "onErrorContainer": core.error.tone(10),
                "background": core.n1.tone(
                    98
                ),  # Original was 99, but that didn't worked in light shades of yellow like: [4294309340, 4294638290, 4294967264]
                "onBackground": core.n1.tone(10),
                "surface": core.n1.tone(98),  # Here also same
                "onSurface": core.n1.tone(10),
                "surfaceVariant": core.n2.tone(90),
                "onSurfaceVariant": core.n2.tone(30),
                "outline": core.n2.tone(50),
                "outlineVariant": core.n2.tone(80),
                "shadow": core.n1.tone(0),
                "scrim": core.n1.tone(0),
                "inverseSurface": core.n1.tone(20),
                "inverseOnSurface": core.n1.tone(95),
                "inversePrimary": core.a1.tone(80),
            }
        )

    @staticmethod
    def dark_from_rgb(rgb: list[int]):
        return Scheme.dark_from_core_palette(CorePalette.of(argb_from_rgba(rgb)))

    @staticmethod
    def dark(argb: int):
        return Scheme.dark_from_core_palette(CorePalette.of(argb))

    @staticmethod
    def dark_content(argb: int):
        return Scheme.dark_from_core_palette(CorePalette.content_of(argb))

    @staticmethod
    def dark_from_core_palette(core: CorePalette):
        return Scheme(
            {
                "primary": core.a1.tone(80),
                "onPrimary": core.a1.tone(20),
                "primaryContainer": core.a1.tone(30),
                "onPrimaryContainer": core.a1.tone(90),
                "secondary": core.a2.tone(80),
                "onSecondary": core.a2.tone(20),
                "secondaryContainer": core.a2.tone(30),
                "onSecondaryContainer": core.a2.tone(90),
                "tertiary": core.a3.tone(80),
                "onTertiary": core.a3.tone(20),
                "tertiaryContainer": core.a3.tone(30),
                "onTertiaryContainer": core.a3.tone(90),
                "error": core.error.tone(80),
                "onError": core.error.tone(20),
                "errorContainer": core.error.tone(30),
                "onErrorContainer": core.error.tone(80),
                "background": core.n1.tone(10),
                "onBackground": core.n1.tone(90),
                "surface": core.n1.tone(10),
                "onSurface": core.n1.tone(90),
                "surfaceVariant": core.n2.tone(30),
                "onSurfaceVariant": core.n2.tone(80),
                "outline": core.n2.tone(60),
                "outlineVariant": core.n2.tone(30),
                "shadow": core.n1.tone(0),
                "scrim": core.n1.tone(0),
                "inverseSurface": core.n1.tone(90),
                "inverseOnSurface": core.n1.tone(20),
                "inversePrimary": core.a1.tone(40),
            }
        )
