import pytest
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.hct.hct import Hct
from materialyoucolor.scheme.scheme_cmf import SchemeCmf


def test_scheme_cmf_single_source():
    hct = Hct.from_int(0xFFFF0000)
    scheme = SchemeCmf(hct, is_dark=False, contrast_level=0.0)
    assert scheme.variant == Variant.CMF
    assert scheme.source_color_hct == hct
    assert scheme.source_color_hcts == [hct]
    expected_error_hue = SchemeCmf.get_error_hue(hct.hue, hct.hue)
    assert scheme.error_palette.hue == pytest.approx(expected_error_hue, abs=0.01)


def test_scheme_cmf_two_sources():
    hct1 = Hct.from_int(0xFFFF0000)  # Red (hue ~27.4)
    hct2 = Hct.from_int(0xFF00FF00)  # Green (hue ~142.1)
    scheme = SchemeCmf([hct1, hct2], is_dark=False, contrast_level=0.0)
    assert scheme.variant == Variant.CMF
    assert scheme.source_color_hcts == [hct1, hct2]
    expected_error_hue = SchemeCmf.get_error_hue(hct1.hue, hct2.hue)
    assert scheme.error_palette.hue == pytest.approx(expected_error_hue, abs=0.01)


def test_scheme_cmf_tokens_2026():
    mdc = MaterialDynamicColors(spec="2026")
    hct1 = Hct.from_int(0xFF4285F4)
    hct2 = Hct.from_int(0xFFEA4335)
    scheme = SchemeCmf([hct1, hct2], is_dark=False, contrast_level=0.0, spec_version="2026")

    # Verify key tokens generate valid ARGB ints
    for attr in [
        "primary",
        "primary_container",
        "secondary",
        "secondary_container",
        "tertiary",
        "tertiary_container",
        "error",
        "error_container",
        "surface",
        "surface_container",
        "highest_surface",
    ]:
        dyn_color = getattr(mdc, attr)
        color_obj = dyn_color(scheme) if callable(dyn_color) else dyn_color
        val = color_obj.get_int(scheme)
        assert (val >> 24) & 0xFF == 0xFF
