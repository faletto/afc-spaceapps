import numpy as np
import pytest

from lunar_listings import terrain


def test_block_mean_nan_and_nodata():
    a = np.arange(16, dtype=np.float32).reshape(4, 4)
    a[0, 0] = -32768
    out = terrain.resample_block_mean(a, (2, 2), nodata=-32768)
    assert out.shape == (2, 2) and out[0, 0] == pytest.approx(np.mean([1, 4, 5]))


def test_slope_of_tilted_plane():
    n = 64
    lat = terrain.lat_centers(n * 1)  # 64 rows over 180 deg: coarse, test equatorial rows only
    cell = 180.0 / n
    dy = terrain.R_M * np.radians(cell)
    tilt = np.tan(np.radians(5.0))
    dem = (np.arange(n)[::-1, None] * dy * tilt * np.ones((1, 2 * n))).astype(np.float64)  # rises northward
    s = terrain.slope_deg_lonlat(dem, cell)
    mid = np.abs(lat) < 60
    assert np.allclose(s[mid], 5.0, atol=0.05)


def test_ew_spacing_shrinks_with_latitude():
    n = 64
    cell = 180.0 / n
    lon_ramp = np.arange(2 * n)[None, :] * 10.0 * np.ones((n, 1))
    s = terrain.slope_deg_lonlat(lon_ramp, cell)
    assert s[n // 2, 5] < s[n // 8, 5]  # steeper toward the poles for the same elevation step


def test_plot_stats_plane_has_zero_roughness():
    n = terrain.CELLS_PER_DEG
    yy, xx = np.mgrid[0 : 2 * n, 0 : 2 * n]
    dem = (3.0 * xx + 2.0 * yy).astype(np.float64)
    st = terrain.global_plot_stats(dem, np.full_like(dem, 4.0, dtype=np.float32), 8.0)
    assert st["roughness_m"].max() < 1e-6
    assert st["relief_m"][0, 0] == pytest.approx(3 * 31 + 2 * 31)
    assert st["safe_area_frac"].min() == 1.0 and st["slope_p90_deg"][0, 0] == pytest.approx(4.0)


def test_hazard_bounds():
    cfg = {"safety": {"slope_p90_range": [0, 30], "roughness_range_m": [0, 50], "relief_range_m": [0, 2000]}}
    assert terrain.hazard_score(0, 0, 0, cfg) == 0
    assert terrain.hazard_score(99, 99, 99999, cfg) == 1


def test_polar_lat_and_grid():
    x, y = terrain.polar_plot_centers(320, 960.0)
    assert x.shape == (320, 320) and y[0, 0] > 0 and x[0, 0] < 0
    assert terrain.polar_lat_deg(0.0, 0.0) == -90
    assert terrain.polar_lat_deg(151_800.0, 0.0) == pytest.approx(-85.0, abs=0.01)
    lat = terrain.polar_lat_deg(x, y)
    assert 70_000 < (lat <= -85).sum() < 85_000  # disc of plots inside 85 deg S


def test_polar_block_stats_chunking_matches_whole():
    rng = np.random.default_rng(0)
    dem = rng.normal(0, 30, (192, 192)).astype(np.float32)
    s = terrain.slope_deg_planar(dem, 20.0)
    a = terrain.polar_block_stats(dem, s, 20.0, 240.0, 8.0, rows_per_chunk=1)
    b = terrain.polar_block_stats(dem, s, 20.0, 240.0, 8.0, rows_per_chunk=99)
    assert a["slope_mean_deg"].shape == (16, 16)
    for k in a:
        assert np.allclose(a[k], b[k])


def test_planar_slope_of_ramp():
    ramp = np.tile(np.arange(50) * 20.0 * np.tan(np.radians(6)), (50, 1))
    assert terrain.slope_deg_planar(ramp, 20.0).mean() == pytest.approx(6.0, abs=0.01)
