import numpy as np
import pytest

from lunar_listings import config, ephemeris, visibility

CFG = config.load()


@pytest.fixture(scope="module")
def eph():
    return ephemeris.load()


def _ref(lat, lon, hz, eph):
    month = visibility.month_of_hour(2028, len(eph["tsi"]))
    return visibility.site_stats_ref(lat, lon, hz, eph["sun_xyz"], eph["earth_xyz"], eph["earth_dist_m"],
                                     eph["tsi"], eph["r_sun_km"], CFG, month)


def test_kernel_matches_reference(eph):
    rng = np.random.default_rng(1)
    lat = np.array([0.0, 45.0, -89.0, -85.0, 30.0])
    lon = np.array([0.0, 120.0, 10.0, -50.0, 200.0])
    hz = np.zeros((5, 180))
    hz[2:4] = rng.uniform(-1, 4, (2, 180))  # rugged polar sites
    k = visibility.site_stats(lat, lon, hz, eph, CFG)
    for i in range(5):
        r = _ref(lat[i], lon[i], hz[i], eph)
        for key in visibility.KEYS:
            assert k[key][i] == pytest.approx(r[key], rel=1e-9, abs=1e-9), (i, key)
        assert np.allclose(k["monthly_sunlit"][i], r["monthly_sunlit"])
        assert np.allclose(k["monthly_earth"][i], r["monthly_earth"])


def test_equator_roughly_half_lit_and_hot(eph):
    r = _ref(0.0, 0.0, np.zeros(180), eph)
    assert 0.47 < r["sunlit_frac"] < 0.53
    assert 14 * 24 < r["longest_dark_h"] < 16 * 24
    assert 360 < r["temp_max_k"] < 400  # subsolar ~ 390 K with these params
    assert r["earth_frac"] > 0.95  # near-side centre


def test_far_side_never_sees_earth(eph):
    r = _ref(0.0, 180.0, np.zeros(180), eph)
    assert r["earth_frac"] < 0.01


def test_psr_floor_and_dark(eph):
    hz = np.full(180, 60.0)  # walled-in site: Sun never above 60 deg wall
    r = _ref(-89.0, 0.0, hz, eph)
    assert r["sunlit_frac"] == 0 and r["temp_max_k"] == 40 and r["longest_dark_h"] == 8784


def test_partial_year_window_parity(eph):
    """A window missing most months must not crash the kernel and must match the reference (NaN months)."""
    sl = slice(0, 24 * 40)
    w = {k: v[sl] for k, v in eph.items()}
    month = visibility.month_of_hour(2028, len(w["tsi"]))
    k = visibility.site_stats(np.array([10.0]), np.array([20.0]), np.zeros((1, 180)), w, CFG)
    r = visibility.site_stats_ref(10.0, 20.0, np.zeros(180), w["sun_xyz"], w["earth_xyz"], w["earth_dist_m"],
                                  w["tsi"], w["r_sun_km"], CFG, month)
    assert np.allclose(k["monthly_sunlit"][0], r["monthly_sunlit"], equal_nan=True)
    assert np.isnan(k["monthly_sunlit"][0, 5]) and k["sunlit_frac"][0] == pytest.approx(r["sunlit_frac"])
