from __future__ import annotations

from typing import List

from materialyoucolor.dynamiccolor.color_spec import (
    COLOR_NAMES,
    ColorSpecDelegate,
    get_spec,
)
from materialyoucolor.dynamiccolor.dynamic_color import DynamicColor


class MaterialDynamicColors:
    content_accent_tone_delta = 15.0

    def __init__(self, spec="2025"):
        self.color_spec: ColorSpecDelegate = get_spec(spec)
        for name in COLOR_NAMES:
            setattr(self, name, getattr(self.color_spec, name)())

    @property
    def all_colors(self) -> List[DynamicColor]:
        colors = [getattr(self, _) for _ in COLOR_NAMES]
        return [c for c in colors if c is not None]

# backward compatibility class attrs
_spec = get_spec("2025")
for name in COLOR_NAMES:
    setattr(MaterialDynamicColors, name, getattr(_spec, name)())
