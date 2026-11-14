"""Science sanity checks (req §9) on real outputs. Skipped when data/work has not been built."""
from pathlib import Path

import numpy as np
import pytest

from lunar_listings import config, ephemeris, plots

WORK = Path(__file__).resolve().parents[2] / "data" / "work"
pytestmark = pytest.mark.skipif(not (WORK / "terrain_global.npz").exists(), reason="real terrain not built")


@pytest.fixture(scope="module")
def tab():
    return plots.build_global(config.load(), WORK)


def sel(t, lat, lon, dlat, dlon):
    return (abs(t["lat"] - lat) <= dlat) & (abs(t["lon"] - lon) <= dlon)


def test_counts_and_areas(tab):
    assert tab["lat"].size == 64800
    assert abs(tab["area_km2"].sum() - 4 * np.pi * 1737.4**2) < 100  # km2
    assert tab["landing_safe"].mean() > 0.5


def test_nearside_far_side_limb(tab):
    assert tab["earth_frac"][sel(tab, 0, 0, 20, 20)].mean() >= 0.99
    assert tab["earth_frac"][sel(tab, 0, 180, 20, 20)].max() <= 0.01
    limb = tab["earth_frac"][sel(tab, 0, 90, 5, 3)]
    assert 0.1 < limb.mean() < 0.9


def test_equatorial_sun_and_dark(tab):
    eq = sel(tab, 0, 0, 10, 180)
    assert tab["sunlit_frac"][eq].mean() == pytest.approx(0.5, abs=0.02)
    assert tab["longest_dark_h"][eq].mean() == pytest.approx(355, abs=10)


def test_tsi_range():
    t = ephemeris.load()["tsi"]
    assert 1300 <= t.min() and t.max() <= 1420  # spec 1320-1412; see Q-P2


def test_equatorial_temperature(tab):
    eq = sel(tab, 0, 0, 5, 180)
    assert tab["temp_max_k"][eq].max() == pytest.approx(390, abs=10)
    assert 95 <= tab["temp_min_k"][eq].min() and tab["temp_min_k"][eq].max() <= 100


def test_steep_terrain_not_landable(tab):
    steep = tab["slope_mean_deg"] > 20
    assert steep.any() and not tab["landing_safe"][steep].any()
