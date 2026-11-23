from materialyoucolor.quantize import QuantizeCelebi, QuantizeWsmeans

RED = 0xFFFF0000
GREEN = 0xFF00FF00
BLUE = 0xFF0000FF


def create_gradient_pixels():
    pixels = []
    for r in range(0, 256, 16):
        for g in range(0, 256, 16):
            b = (r * 3 + g * 5) & 0xFF
            pixels.append(((0xFF << 24) | (r << 16) | (g << 8) | b) & 0xFFFFFFFF)
    return pixels


def test_quantize_celebi_basic():
    # 1R
    ans = QuantizeCelebi([RED], 128)
    assert len(ans) == 1
    assert ans[RED] == 1

    # 1G
    ans = QuantizeCelebi([GREEN], 128)
    assert len(ans) == 1
    assert ans[GREEN] == 1

    # 1B
    ans = QuantizeCelebi([BLUE], 128)
    assert len(ans) == 1
    assert ans[BLUE] == 1

    # 5B
    ans = QuantizeCelebi([BLUE] * 5, 128)
    assert len(ans) == 1
    assert ans[BLUE] == 5

    # 2R 3G
    ans = QuantizeCelebi([RED, RED, GREEN, GREEN, GREEN], 128)
    assert len(ans) == 2
    assert ans[RED] == 2
    assert ans[GREEN] == 3

    # 1R 1G 1B
    ans = QuantizeCelebi([RED, GREEN, BLUE], 128)
    assert len(ans) == 3
    assert ans[RED] == 1
    assert ans[GREEN] == 1
    assert ans[BLUE] == 1


def test_quantize_celebi_empty():
    ans = QuantizeCelebi([], 128)
    assert ans == {}


def test_quantize_celebi_rgb_tuples():
    # Calling with [[r, g, b], ...] tuples / lists
    pixels = [[255, 0, 0], [0, 255, 0], [0, 0, 255]]
    ans = QuantizeCelebi(pixels, 128)
    assert len(ans) == 3
    assert ans[RED] == 1
    assert ans[GREEN] == 1
    assert ans[BLUE] == 1


def test_quantize_celebi_deterministic():
    pixels = create_gradient_pixels()
    first = QuantizeCelebi(pixels, 32)
    second = QuantizeCelebi(pixels, 32)
    assert list(first.items()) == list(second.items())


def test_quantize_wsmeans_deterministic():
    pixels = create_gradient_pixels()
    first = QuantizeWsmeans(pixels, [], 16)
    second = QuantizeWsmeans(pixels, [], 16)
    assert list(first.items()) == list(second.items())
