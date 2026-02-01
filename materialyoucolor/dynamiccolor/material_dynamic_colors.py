from __future__ import annotations

from typing import List, Optional

from materialyoucolor.dynamiccolor.color_spec import (
    COLOR_NAMES,
    ColorSpecDelegate,
    get_spec,
)
from materialyoucolor.dynamiccolor.dynamic_color import DynamicColor
from materialyoucolor.dynamiccolor.dynamic_scheme import DynamicScheme


class MaterialDynamicColors:
    content_accent_tone_delta = 15.0

    def __init__(self, spec="2025"):
        self.color_spec: ColorSpecDelegate = get_spec(spec)

    # define them dynamically
    for color_name in COLOR_NAMES:
        exec(
            f"@property\ndef {color_name}(self) -> DynamicColor:\n\treturn self.color_spec.{color_name}()"
        )

    @property
    def all_colors(self) -> List[DynamicColor]:
        colors = [getattr(self, _) for _ in COLOR_NAMES]
        return [c for c in colors if c is not None]
