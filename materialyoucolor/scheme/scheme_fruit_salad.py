from materialyoucolor.dynamiccolor.dynamic_scheme import (
    DynamicScheme,
    Platform,
    SpecVersion,
)
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct


class SchemeFruitSalad(DynamicScheme):
    def __init__(
        self,
        source_color_hct: Hct,
        is_dark: bool,
        contrast_level: float,
        spec_version: SpecVersion = DynamicScheme.DEFAULT_SPEC_VERSION,
        platform: Platform = DynamicScheme.DEFAULT_PLATFORM,
    ):
        super().__init__(
            source_color_hct=source_color_hct,
            variant=Variant.FRUIT_SALAD,
            contrast_level=contrast_level,
            is_dark=is_dark,
            platform=platform,
            spec_version=spec_version,
        )
