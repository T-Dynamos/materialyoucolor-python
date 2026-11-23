import pytest
from materialyoucolor.contrast.contrast import Contrast
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.hct.hct import Hct
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot


def test_material_dynamic_colors_properties():
    mdc = MaterialDynamicColors()

    assert mdc.primary is not None
    assert mdc.primary_container is not None
    assert mdc.highest_surface is not None
    assert mdc.surface_dim is not None
    assert mdc.surface_bright is not None


def test_material_dynamic_colors_all_specs():
    for spec in ["2021", "2025", "2026"]:
        mdc = MaterialDynamicColors(spec=spec)
        scheme_l = SchemeTonalSpot(
            Hct.from_int(0xFF4285F4),
            is_dark=False,
            contrast_level=0.0,
            spec_version=spec,
        )
        scheme_d = SchemeTonalSpot(
            Hct.from_int(0xFF4285F4),
            is_dark=True,
            contrast_level=0.0,
            spec_version=spec,
        )

        # Primary and on_primary should meet 4.5:1 contrast
        p_tone_l = mdc.primary.get_hct(scheme_l).tone
        on_p_tone_l = mdc.on_primary.get_hct(scheme_l).tone
        assert Contrast.ratio_of_tones(p_tone_l, on_p_tone_l) >= 4.5

        p_tone_d = mdc.primary.get_hct(scheme_d).tone
        on_p_tone_d = mdc.on_primary.get_hct(scheme_d).tone
        assert Contrast.ratio_of_tones(p_tone_d, on_p_tone_d) >= 4.5
