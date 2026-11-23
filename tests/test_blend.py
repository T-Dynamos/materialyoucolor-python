from materialyoucolor.blend.blend import Blend

RED = 0xFFFF0000
BLUE = 0xFF0000FF
GREEN = 0xFF00FF00
YELLOW = 0xFFFFFF00


def test_blend_harmonize():
    assert Blend.harmonize(RED, BLUE) == 0xFFFB0057
    assert Blend.harmonize(RED, GREEN) == 0xFFD85600
    assert Blend.harmonize(RED, YELLOW) == 0xFFD85600

    assert Blend.harmonize(BLUE, GREEN) == 0xFF0047A3
    assert Blend.harmonize(BLUE, RED) == 0xFF5700DC
    assert Blend.harmonize(BLUE, YELLOW) == 0xFF0047A3

    assert Blend.harmonize(GREEN, BLUE) == 0xFF00FC94
    assert Blend.harmonize(GREEN, RED) == 0xFFB1F000
    assert Blend.harmonize(GREEN, YELLOW) == 0xFFB1F000

    assert Blend.harmonize(YELLOW, BLUE) == 0xFFEBFFBA
    assert Blend.harmonize(YELLOW, GREEN) == 0xFFEBFFBA
    assert Blend.harmonize(YELLOW, RED) == 0xFFFFF6E3


def test_blend_cam16_ucs():
    res = Blend.cam16_ucs(RED, BLUE, 0.5)
    assert (res >> 24) & 0xFF == 0xFF
