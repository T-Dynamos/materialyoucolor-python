from materialyoucolor.score.score import Score, ScoreOptions


def test_prioritizes_chroma():
    colors = {
        0xFF000000: 1,
        0xFFFFFFFF: 1,
        0xFF0000FF: 1,
    }
    ranked = Score.score(colors, ScoreOptions(desired=4))
    assert len(ranked) == 1
    assert ranked[0] == 0xFF0000FF


def test_prioritizes_chroma_when_proportions_equal():
    colors = {
        0xFFFF0000: 1,
        0xFF00FF00: 1,
        0xFF0000FF: 1,
    }
    ranked = Score.score(colors, desired=4)
    assert len(ranked) == 3
    assert ranked[0] == 0xFFFF0000
    assert ranked[1] == 0xFF00FF00
    assert ranked[2] == 0xFF0000FF


def test_generates_gblue_when_no_colors():
    colors = {
        0xFF000000: 1,
    }
    ranked = Score.score(colors, {"desired": 4})
    assert len(ranked) == 1
    assert ranked[0] == 0xFF4285F4


def test_dedupes_nearby_hues():
    colors = {
        0xFF008772: 1,  # H 180 C 42 T 50
        0xFF318477: 1,  # H 184 C 35 T 50
    }
    ranked = Score.score(colors, desired=4)
    assert len(ranked) == 1
    assert ranked[0] == 0xFF008772


def test_maximizes_hue_distance():
    colors = {
        0xFF008772: 1,
        0xFF008587: 1,
        0xFF007EBC: 1,
    }
    ranked = Score.score(colors, desired=2)
    assert len(ranked) == 2
    assert ranked[0] == 0xFF007EBC
    assert ranked[1] == 0xFF008772
