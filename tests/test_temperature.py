import pytest
from materialyoucolor.hct.hct import Hct
from materialyoucolor.temperature.temperature_cache import TemperatureCache

BLUE = 0xFF0000FF
RED = 0xFFFF0000
GREEN = 0xFF00FF00
WHITE = 0xFFFFFFFF
BLACK = 0xFF000000


def test_raw_temperature():
    assert TemperatureCache.raw_temperature(Hct.from_int(BLUE)) == pytest.approx(
        -1.393, abs=0.01
    )
    assert TemperatureCache.raw_temperature(Hct.from_int(RED)) == pytest.approx(
        2.351, abs=0.01
    )
    assert TemperatureCache.raw_temperature(Hct.from_int(GREEN)) == pytest.approx(
        -0.267, abs=0.01
    )
    assert TemperatureCache.raw_temperature(Hct.from_int(WHITE)) == pytest.approx(
        -0.5, abs=0.01
    )
    assert TemperatureCache.raw_temperature(Hct.from_int(BLACK)) == pytest.approx(
        -0.5, abs=0.01
    )


def test_input_relative_temperature():
    assert TemperatureCache(Hct.from_int(BLUE)).input_relative_temperature == pytest.approx(
        0.0, abs=0.01
    )
    assert TemperatureCache(Hct.from_int(RED)).input_relative_temperature == pytest.approx(
        1.0, abs=0.01
    )
    assert TemperatureCache(Hct.from_int(GREEN)).input_relative_temperature == pytest.approx(
        0.467, abs=0.01
    )
    assert TemperatureCache(Hct.from_int(WHITE)).input_relative_temperature == pytest.approx(
        0.5, abs=0.01
    )
    assert TemperatureCache(Hct.from_int(BLACK)).input_relative_temperature == pytest.approx(
        0.5, abs=0.01
    )


def test_complement():
    assert TemperatureCache(Hct.from_int(BLUE)).complement.to_int() == 0xFF9D0002
    assert TemperatureCache(Hct.from_int(RED)).complement.to_int() == 0xFF007BFC
    assert TemperatureCache(Hct.from_int(GREEN)).complement.to_int() == 0xFFFFD2C9
    assert TemperatureCache(Hct.from_int(WHITE)).complement.to_int() == 0xFFFFFFFF
    assert TemperatureCache(Hct.from_int(BLACK)).complement.to_int() == 0xFF000000


def test_analogous():
    blue_analogous = [c.to_int() for c in TemperatureCache(Hct.from_int(BLUE)).analogous()]
    assert blue_analogous[0] == 0xFF00590C
    assert blue_analogous[1] == 0xFF00564E
    assert blue_analogous[2] == 0xFF0000FF
    assert blue_analogous[3] == 0xFF6700CC
    assert blue_analogous[4] == 0xFF81009F
