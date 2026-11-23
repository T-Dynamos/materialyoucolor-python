from __future__ import annotations

from materialyoucolor.dynamiccolor.dynamic_scheme import (
    DynamicScheme,
    Platform,
    SpecVersion,
)
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct


class SchemeNeutral(DynamicScheme):
    def __init__(
        self,
        source_color_hct: Hct | list[Hct] | None = None,
        is_dark: bool = False,
        contrast_level: float = 0.0,
        spec_version: SpecVersion = DynamicScheme.DEFAULT_SPEC_VERSION,
        platform: Platform = DynamicScheme.DEFAULT_PLATFORM,
        source_color_hcts: list[Hct] | None = None,
    ):
        super().__init__(
            source_color_hct=source_color_hct,
            source_color_hcts=source_color_hcts,
            variant=Variant.NEUTRAL,
            contrast_level=contrast_level,
            is_dark=is_dark,
            platform=platform,
            spec_version=spec_version,
        )
