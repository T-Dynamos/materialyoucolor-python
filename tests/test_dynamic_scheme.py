import pytest
from materialyoucolor.dynamiccolor.dynamic_scheme import DynamicScheme
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct
from materialyoucolor.scheme import (
    SchemeContent,
    SchemeExpressive,
    SchemeFidelity,
    SchemeFruitSalad,
    SchemeMonochrome,
    SchemeNeutral,
    SchemeRainbow,
    SchemeTonalSpot,
    SchemeVibrant,
)
from materialyoucolor.scheme.scheme_cmf import SchemeCmf


def test_get_rotated_hue():
    # 0 length input
    hue = DynamicScheme.get_rotated_hue(Hct.from_hct(43, 16, 16), [], [])
    assert hue == pytest.approx(43, abs=0.4)

    # 1 length input no rotation
    hue = DynamicScheme.get_rotated_hue(Hct.from_hct(43, 16, 16), [0], [0])
    assert hue == pytest.approx(43, abs=0.4)

    # input length mismatch
    hue = DynamicScheme.get_rotated_hue(Hct.from_hct(43, 16, 16), [0], [0, 1])
    assert hue == pytest.approx(43, abs=0.4)

    # on boundary rotation
    hue = DynamicScheme.get_rotated_hue(
        Hct.from_hct(43, 16, 16), [0, 42, 360], [0, 15, 0]
    )
    assert hue == pytest.approx(43 + 15, abs=0.4)

    # larger than 360 wraps
    hue = DynamicScheme.get_rotated_hue(
        Hct.from_hct(43, 16, 16), [0, 42, 360], [0, 480, 0]
    )
    assert hue == pytest.approx(163, abs=0.4)


def test_scheme_variants_instantiation():
    hct = Hct.from_int(0xFF0000FF)
    schemes = [
        SchemeContent,
        SchemeExpressive,
        SchemeFidelity,
        SchemeFruitSalad,
        SchemeMonochrome,
        SchemeNeutral,
        SchemeRainbow,
        SchemeTonalSpot,
        SchemeVibrant,
        SchemeCmf,
    ]
    for scheme_cls in schemes:
        for spec in ["2021", "2025", "2026"]:
            if scheme_cls == SchemeCmf and spec != "2026":
                continue
            for platform in ["phone", "watch"]:
                for is_dark in [False, True]:
                    scheme = scheme_cls(
                        hct,
                        is_dark,
                        0.0,
                        spec_version=spec,
                        platform=platform,
                    )
                    assert scheme.primary_palette is not None
                    assert scheme.secondary_palette is not None
                    assert scheme.tertiary_palette is not None
                    assert scheme.neutral_palette is not None
                    assert scheme.neutral_variant_palette is not None
                    assert scheme.error_palette is not None


def test_scheme_multi_source_color_support():
    hct1 = Hct.from_int(0xFFFF0000)
    hct2 = Hct.from_int(0xFF00FF00)
    scheme = SchemeTonalSpot(
        [hct1, hct2],
        is_dark=False,
        contrast_level=0.0,
        spec_version="2026",
    )
    assert scheme.source_color_hcts == [hct1, hct2]
    assert scheme.source_color_hct == hct1
    assert scheme.source_color_argb == hct1.to_int()
