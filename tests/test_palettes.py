from materialyoucolor.palettes.core_palette import CorePalette
from materialyoucolor.palettes.tonal_palette import TonalPalette


def test_tonal_palette_of_blue():
    blue = TonalPalette.from_int(0xFF0000FF)
    assert blue.tone(100) == 0xFFFFFFFF
    assert blue.tone(95) == 0xFFF1EFFF
    assert blue.tone(90) == 0xFFE0E0FF
    assert blue.tone(80) == 0xFFBEC2FF
    assert blue.tone(70) == 0xFF9DA3FF
    assert blue.tone(60) == 0xFF7C84FF
    assert blue.tone(50) == 0xFF5A64FF
    assert blue.tone(40) == 0xFF343DFF
    assert blue.tone(30) == 0xFF0000EF
    assert blue.tone(20) == 0xFF0001AC
    assert blue.tone(10) == 0xFF00006E
    assert blue.tone(0) == 0xFF000000


def test_core_palette_of_blue():
    core = CorePalette.of(0xFF0000FF)
    assert core.a1.tone(100) == 0xFFFFFFFF
    assert core.a1.tone(95) == 0xFFF1EFFF
    assert core.a1.tone(90) == 0xFFE0E0FF
    assert core.a1.tone(80) == 0xFFBEC2FF
    assert core.a1.tone(70) == 0xFF9DA3FF
    assert core.a1.tone(60) == 0xFF7C84FF
    assert core.a1.tone(50) == 0xFF5A64FF
    assert core.a1.tone(40) == 0xFF343DFF
    assert core.a1.tone(30) == 0xFF0000EF
    assert core.a1.tone(20) == 0xFF0001AC
    assert core.a1.tone(10) == 0xFF00006E
    assert core.a1.tone(0) == 0xFF000000

    assert core.a2.tone(100) == 0xFFFFFFFF
    assert core.a2.tone(95) == 0xFFF1EFFF
    assert core.a2.tone(90) == 0xFFE1E0F9
    assert core.a2.tone(80) == 0xFFC5C4DD
    assert core.a2.tone(70) == 0xFFA9A9C1
    assert core.a2.tone(60) == 0xFF8F8FA6
    assert core.a2.tone(50) == 0xFF75758B
    assert core.a2.tone(40) == 0xFF5C5D72
    assert core.a2.tone(30) == 0xFF444559
    assert core.a2.tone(20) == 0xFF2E2F42
    assert core.a2.tone(10) == 0xFF191A2C
    assert core.a2.tone(0) == 0xFF000000


def test_core_palette_content_of_blue():
    core = CorePalette.content_of(0xFF0000FF)
    assert core.a1.tone(100) == 0xFFFFFFFF
    assert core.a1.tone(95) == 0xFFF1EFFF
    assert core.a1.tone(90) == 0xFFE0E0FF
    assert core.a1.tone(80) == 0xFFBEC2FF
    assert core.a1.tone(70) == 0xFF9DA3FF
    assert core.a1.tone(60) == 0xFF7C84FF
    assert core.a1.tone(50) == 0xFF5A64FF
    assert core.a1.tone(40) == 0xFF343DFF
    assert core.a1.tone(30) == 0xFF0000EF
    assert core.a1.tone(20) == 0xFF0001AC
    assert core.a1.tone(10) == 0xFF00006E
    assert core.a1.tone(0) == 0xFF000000

    assert core.a2.tone(100) == 0xFFFFFFFF
    assert core.a2.tone(95) == 0xFFF1EFFF
    assert core.a2.tone(90) == 0xFFE0E0FF
    assert core.a2.tone(80) == 0xFFC1C3F4
    assert core.a2.tone(70) == 0xFFA5A7D7
    assert core.a2.tone(60) == 0xFF8B8DBB
    assert core.a2.tone(50) == 0xFF7173A0
    assert core.a2.tone(40) == 0xFF585B86
    assert core.a2.tone(30) == 0xFF40436D
    assert core.a2.tone(20) == 0xFF2A2D55
