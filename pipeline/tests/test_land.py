import numpy as np
import pytest

from lunar_listings import config, land

CFG = config.load()


def test_great_circle():
    assert land.great_circle_km(0, 0, 0, 90) == pytest.approx(np.pi / 2 * 1737.4)
    assert land.great_circle_km(10, 20, 10, 20) == 0
    assert land.great_circle_km(90, 0, -90, 0) == pytest.approx(np.pi * 1737.4)


def test_landmark_score_and_nearby():
    lm = land.load_landmarks()
    assert len(lm["name"]) > 1000 and "Apollo 11" in lm["name"]
    lat, lon = np.array([0.674, 0.0, -89.0]), np.array([23.473, 180.0, 0.0])
    s, near = land.landmark_score_and_nearby(lat, lon, lm, CFG)
    assert s[0] == pytest.approx(1.0) and lm["name"][near[0, 0]] in ("Apollo 11",)
    assert 0 <= s.min() and s.max() <= 1
    assert (near[:, 0] >= -1).all()


def test_land_type_priority():
    n = np.array([0.005, 0.8, 0.5, 0.5, 0.5, 0.5])
    lat = np.full(6, -87.0)
    lon = np.array([0, 0, 120, 0, 0, 0.0])
    elev = np.array([0, 0, 0, 0, 0, -5000.0])
    elev_ref = np.append(elev, np.full(20, 0.0))  # median 0
    tpi = np.array([0, 0, 0, 300, -300, 0.0])
    full = lambda a, fill: np.append(a, np.full(20, fill))
    t = land.land_type(full(n, 0.5), full(lat, -87.0), full(lon, 0.0), elev_ref, full(tpi, 0.0), CFG, polar=True)[:6]
    assert [land.LAND_TYPES[i] for i in t] == ["psr", "peak_of_light", "far_side", "crater_rim", "crater_floor", "mare"]


def test_tpi_flat_zero_and_bump():
    d = np.zeros((64, 128))
    assert np.allclose(land.tpi_cells(d, 5.0), 0)
    d[32, 64] = 500
    assert land.tpi_cells(d, 5.0)[32, 64] > 300
