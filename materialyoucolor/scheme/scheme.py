from materialyoucolor.palettes.core_palette import CorePalette


class Scheme:
    def __init__(self, props: dict):
        self.props = props

    @property
    def primary(self) -> int:
        return self.props["primary"]

    @property
    def on_primary(self) -> int:
        return self.props["onPrimary"]

    @property
    def primary_container(self) -> int:
        return self.props["primaryContainer"]

    @property
    def on_primary_container(self) -> int:
        return self.props["onPrimaryContainer"]

    @property
    def secondary(self) -> int:
        return self.props["secondary"]

    @property
    def on_secondary(self) -> int:
        return self.props["onSecondary"]

    @property
    def secondary_container(self) -> int:
        return self.props["secondaryContainer"]

    @property
    def on_secondary_container(self) -> int:
        return self.props["onSecondaryContainer"]

    @property
    def tertiary(self) -> int:
        return self.props["tertiary"]

    @property
    def on_tertiary(self) -> int:
        return self.props["onTertiary"]

    @property
    def tertiary_container(self) -> int:
        return self.props["tertiaryContainer"]

    @property
    def on_tertiary_container(self) -> int:
        return self.props["onTertiaryContainer"]

    @property
    def error(self) -> int:
        return self.props["error"]

    @property
    def on_error(self) -> int:
        return self.props["onError"]

    @property
    def error_container(self) -> int:
        return self.props["errorContainer"]

    @property
    def on_error_container(self) -> int:
        return self.props["onErrorContainer"]

    @property
    def background(self) -> int:
        return self.props["background"]

    @property
    def on_background(self) -> int:
        return self.props["onBackground"]

    @property
    def surface(self) -> int:
        return self.props["surface"]

    @property
    def on_surface(self) -> int:
        return self.props["onSurface"]

    @property
    def surface_variant(self) -> int:
        return self.props["surfaceVariant"]

    @property
    def on_surface_variant(self) -> int:
        return self.props["onSurfaceVariant"]

    @property
    def outline(self) -> int:
        return self.props["outline"]

    @property
    def outline_variant(self) -> int:
        return self.props["outlineVariant"]

    @property
    def shadow(self) -> int:
        return self.props["shadow"]

    @property
    def scrim(self) -> int:
        return self.props["scrim"]

    @property
    def inverse_surface(self) -> int:
        return self.props["inverseSurface"]

    @property
    def inverse_on_surface(self) -> int:
        return self.props["inverseOnSurface"]

    @property
    def inverse_primary(self) -> int:
        return self.props["inversePrimary"]

    @staticmethod
    def light(argb: int) -> "Scheme":
        return Scheme.light_from_core_palette(CorePalette.of(argb))

    @staticmethod
    def dark(argb: int) -> "Scheme":
        return Scheme.dark_from_core_palette(CorePalette.of(argb))

    @staticmethod
    def light_content(argb: int) -> "Scheme":
        return Scheme.light_from_core_palette(CorePalette.content_of(argb))

    @staticmethod
    def dark_content(argb: int) -> "Scheme":
        return Scheme.dark_from_core_palette(CorePalette.content_of(argb))

    @staticmethod
    def light_from_core_palette(core: CorePalette) -> "Scheme":
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
                "background": core.n1.tone(99),
                "onBackground": core.n1.tone(10),
                "surface": core.n1.tone(99),
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
    def dark_from_core_palette(core: CorePalette) -> "Scheme":
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

    def to_json(self) -> dict:
        return self.props
