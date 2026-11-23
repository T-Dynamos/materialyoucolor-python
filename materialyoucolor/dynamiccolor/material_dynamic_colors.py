from __future__ import annotations

from typing import TYPE_CHECKING, List

from materialyoucolor.dynamiccolor.color_spec import (
    COLOR_NAMES,
    ColorSpecDelegate,
    get_spec,
)
from materialyoucolor.dynamiccolor.dynamic_color import DynamicColor

if TYPE_CHECKING:
    from materialyoucolor.dynamiccolor.dynamic_scheme import DynamicScheme


import re

def _camel_to_snake(camel_str: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

def _snake_to_camel(snake_str: str) -> str:
    parts = snake_str.split('_')
    return parts[0] + ''.join(x.title() for x in parts[1:])

class MaterialDynamicColors:
    content_accent_tone_delta = 15.0

    def __init__(self, spec="2026"):
        self.color_spec: ColorSpecDelegate = get_spec(spec)
        for name in COLOR_NAMES:
            color = getattr(self.color_spec, name)()
            setattr(self, name, color)
            snake_name = _camel_to_snake(name)
            if snake_name != name:
                setattr(self, snake_name, color)

    def __getattr__(self, item: str):
        camel = _snake_to_camel(item)
        if camel in self.__dict__:
            return self.__dict__[camel]
        raise AttributeError(f"'MaterialDynamicColors' object has no attribute '{item}'")

    def highest_surface(self, s: "DynamicScheme") -> DynamicColor:
        return self.color_spec.highestSurface(s)

    @classmethod
    def get_highest_surface(cls, s: "DynamicScheme") -> DynamicColor:
        return get_spec("2026").highestSurface(s)

    @property
    def all_colors(self) -> List[DynamicColor]:
        colors = [getattr(self, _) for _ in COLOR_NAMES]
        return [c for c in colors if c is not None]


# backward compatibility class attrs
_spec = get_spec("2026")
for name in COLOR_NAMES:
    _val = getattr(_spec, name)()
    setattr(MaterialDynamicColors, name, _val)
    _snake = _camel_to_snake(name)
    if _snake != name:
        setattr(MaterialDynamicColors, _snake, _val)
