from materialyoucolor.dislike.dislike_analyzer import DislikeAnalyzer
from materialyoucolor.hct.hct import Hct


def test_likes_monk_skin_tone_scale():
    monk_skin_tone_scale_colors = [
        0xFFF6EDE4,
        0xFFF3E7DB,
        0xFFF7EAD0,
        0xFFEADABA,
        0xFFD7BD96,
        0xFFA07E56,
        0xFF825C43,
        0xFF604134,
        0xFF3A312A,
        0xFF292420,
    ]
    for color in monk_skin_tone_scale_colors:
        assert not DislikeAnalyzer.is_disliked(Hct.from_int(color))


def test_dislikes_bile_colors():
    unlikable = [
        0xFF95884B,
        0xFF716B40,
        0xFFB08E00,
        0xFF4C4308,
        0xFF464521,
    ]
    for color in unlikable:
        assert DislikeAnalyzer.is_disliked(Hct.from_int(color))


def test_makes_bile_colors_likable():
    unlikable = [
        0xFF95884B,
        0xFF716B40,
        0xFFB08E00,
        0xFF4C4308,
        0xFF464521,
    ]
    for color in unlikable:
        hct = Hct.from_int(color)
        assert DislikeAnalyzer.is_disliked(hct)
        likable = DislikeAnalyzer.fix_if_disliked(hct)
        assert not DislikeAnalyzer.is_disliked(likable)


def test_likes_tone_67_colors():
    color = Hct.from_hct(100.0, 50.0, 67.0)
    assert not DislikeAnalyzer.is_disliked(color)
    assert DislikeAnalyzer.fix_if_disliked(color).to_int() == color.to_int()
