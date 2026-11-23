import pytest
from materialyoucolor.contrast.contrast import Contrast
from materialyoucolor.dynamiccolor.contrast_curve import ContrastCurve


def test_ratio_of_tones_out_of_bounds():
    assert Contrast.ratio_of_tones(-10.0, 110.0) == pytest.approx(21.0, abs=0.01)


def test_lighter_impossible():
    assert Contrast.lighter(90.0, 10.0) == pytest.approx(-1.0, abs=0.001)
    assert Contrast.lighter(110.0, 2.0) == pytest.approx(-1.0, abs=0.001)
    assert Contrast.lighter(-10.0, 2.0) == pytest.approx(-1.0, abs=0.001)


def test_lighter_unsafe():
    assert Contrast.lighter_unsafe(100.0, 2.0) == pytest.approx(100.0, abs=0.001)


def test_darker_impossible():
    assert Contrast.darker(10.0, 20.0) == pytest.approx(-1.0, abs=0.001)
    assert Contrast.darker(110.0, 2.0) == pytest.approx(-1.0, abs=0.001)
    assert Contrast.darker(-10.0, 2.0) == pytest.approx(-1.0, abs=0.001)


def test_darker_unsafe():
    assert Contrast.darker_unsafe(0.0, 2.0) == pytest.approx(0.0, abs=0.001)


def test_contrast_curve():
    curve = ContrastCurve(1.0, 3.0, 4.5, 7.0)
    assert curve.get(-1.0) == 1.0
    assert curve.get(0.0) == 3.0
    assert curve.get(0.5) == 4.5
    assert curve.get(1.0) == 7.0
