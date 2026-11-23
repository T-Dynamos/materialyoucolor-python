import pytest
from materialyoucolor.hct.cam16 import Cam16
from materialyoucolor.hct.hct import Hct
from materialyoucolor.hct.viewing_conditions import ViewingConditions

RED = 0xFFFF0000
GREEN = 0xFF00FF00
BLUE = 0xFF0000FF
WHITE = 0xFFFFFFFF
BLACK = 0xFF000000


def test_cam_from_int():
    cam_red = Cam16.from_int(RED)
    assert cam_red.hue == pytest.approx(27.408, abs=0.01)
    assert cam_red.chroma == pytest.approx(113.358, abs=0.01)
    assert cam_red.j == pytest.approx(46.445, abs=0.01)
    assert cam_red.m == pytest.approx(89.494, abs=0.01)
    assert cam_red.s == pytest.approx(91.890, abs=0.01)
    assert cam_red.q == pytest.approx(105.989, abs=0.01)

    cam_green = Cam16.from_int(GREEN)
    assert cam_green.hue == pytest.approx(142.140, abs=0.01)
    assert cam_green.chroma == pytest.approx(108.410, abs=0.01)
    assert cam_green.j == pytest.approx(79.332, abs=0.01)

    cam_blue = Cam16.from_int(BLUE)
    assert cam_blue.hue == pytest.approx(282.788, abs=0.01)
    assert cam_blue.chroma == pytest.approx(87.231, abs=0.01)
    assert cam_blue.j == pytest.approx(25.466, abs=0.01)

    cam_white = Cam16.from_int(WHITE)
    assert cam_white.hue == pytest.approx(209.492, abs=0.01)
    assert cam_white.chroma == pytest.approx(2.869, abs=0.01)
    assert cam_white.j == pytest.approx(100.0, abs=0.01)

    cam_black = Cam16.from_int(BLACK)
    assert cam_black.hue == pytest.approx(0.0, abs=0.01)
    assert cam_black.chroma == pytest.approx(0.0, abs=0.01)
    assert cam_black.j == pytest.approx(0.0, abs=0.01)


def test_cam_round_trip():
    for color in [RED, GREEN, BLUE, WHITE, BLACK]:
        cam = Cam16.from_int(color)
        assert cam.to_int() == color


def test_hct_basic():
    hct_red = Hct.from_int(RED)
    assert hct_red.to_int() == RED

    # Property modifications
    hct = Hct.from_int(RED)
    hct.hue = 180.0
    assert hct.hue == pytest.approx(180.0, abs=1.0)

    hct.chroma = 30.0
    assert hct.chroma == pytest.approx(30.0, abs=1.0)

    hct.tone = 50.0
    assert hct.tone == pytest.approx(50.0, abs=1.0)


def test_hct_color_predicates():
    assert Hct.is_blue(260.0)
    assert not Hct.is_blue(240.0)
    assert Hct.is_yellow(110.0)
    assert not Hct.is_yellow(130.0)
    assert Hct.is_cyan(180.0)
    assert not Hct.is_cyan(220.0)
