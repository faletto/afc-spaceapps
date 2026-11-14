import numpy as np
import pytest

from lunar_listings import config, horizons, polar

CFG = config.load()


def _dems(fn, near_half=20_000.0, near_res=20.0, far_half=160_000.0, far_res=80.0):
    def grid(half, res):
        n = round(2 * half / res)
        c = (np.arange(n) + 0.5) * res - half
        X, Y = np.meshgrid(c, -c)
        return fn(X, Y).astype(np.float32)
    return horizons.Dems(grid(near_half, near_res), near_half, near_res, grid(far_half, far_res), far_half, far_res)


def test_flat_plane_horizon_is_curvature_only():
    d = _dems(lambda X, Y: 0 * X)
    hz = horizons.compute(np.array([0.0]), np.array([5000.0]), np.array([0.0]), d, CFG)
    # observer 2 m up on a flat plane: skyline is the dip from the mast, tiny and negative
    assert hz.max() < 0.01 and hz.min() > -0.1


def test_wall_in_known_direction():
    # 500 m high wall for x > 3000 (east of the observer at the origin-ish)
    d = _dems(lambda X, Y: np.where(X > 3000, 500.0, 0.0))
    x0, y0 = 0.0, 5000.0
    lon = np.degrees(np.arctan2(x0, y0))
    hz = horizons.compute(np.array([x0]), np.array([y0]), np.array([lon]), d, CFG)[0]
    east_k = int(round(((np.degrees(np.arctan2(1, 0)) - lon) % 360) / 2))  # map +x direction as a bearing
    want = np.degrees(np.arctan2(500 - 2, 3000))
    assert hz[east_k] == pytest.approx(want, abs=0.1)
    west_k = (east_k + 90) % 180
    assert hz[west_k] < 0.2


def test_cone_matches_dense_bruteforce_within_0p05_deg():
    H, a = 800.0, 4000.0  # cone of height H, base radius a, centred 6 km east of the observer
    cx = 6000.0
    prof = lambda r: np.clip(H * (1 - np.abs(r) / a), 0, 0.9 * H)  # noqa: E731  (frustum: sharp apex is below the 20 m raster's resolving power)
    d = _dems(lambda X, Y: prof(np.hypot(X - cx, Y)))
    x0, y0 = 0.0, 0.0
    fast = horizons.compute(np.array([x0]), np.array([y0]), np.array([0.0]), d, CFG)[0]
    dense = horizons.compute_ref(x0, y0, 0.0, d, CFG, ray_step_m=5.0)
    assert np.nanmax(np.abs(fast - dense)) <= 0.05
    # analytic: toward the cone, skyline = max over d of atan((H(1-|d-cx|/a) - h0)/d) (flat otherwise)
    dd = np.linspace(cx - a, cx + a, 200001)
    an = np.degrees(np.max(np.arctan2(prof(dd - cx) - 2.0 - dd**2 / (2 * horizons.R_M), dd)))
    k = round(((90 - 0.0) % 360) / 2)  # bearing from map +y: +x is angle 90 (lon=0)
    assert fast[k] == pytest.approx(an, abs=0.05)


def test_numba_matches_reference_on_rough_terrain():
    rng = np.random.default_rng(3)
    base = rng.normal(0, 1, (64, 64))
    from scipy.ndimage import gaussian_filter, zoom

    f = lambda X, Y: zoom(gaussian_filter(base, 3) * 300, 1, order=1)[
        np.clip(((Y + 160000) / 5000).astype(int) % 64, 0, 63), np.clip(((X + 160000) / 5000).astype(int) % 64, 0, 63)]
    d = _dems(f)
    xs, ys = np.array([1000.0, -7000.0]), np.array([2000.0, 4000.0])
    lons = np.degrees(np.arctan2(xs, ys))
    fast = horizons.compute(xs, ys, lons, d, CFG)
    for i in range(2):
        ref = horizons.compute_ref(xs[i], ys[i], lons[i], d, CFG)
        assert np.nanmax(np.abs(fast[i] - ref)) < 1e-3


def test_ridge_to_the_east_bearing_orientation():
    """A ridge east of a southern-polar site must show up at bearing ~90 deg from local north."""
    lat, lon = -87.0, 40.0
    x0, y0 = polar.lonlat_to_xy(lat, lon)
    ex, ey = polar.ray_direction(lon, 90)  # unit vector of "east" in the map
    d = _dems(lambda X, Y: np.where(((X - x0) * ex + (Y - y0) * ey > 4000) & (np.hypot(X - x0, Y - y0) < 9000), 400.0, 0.0),
              near_half=30_000.0)
    hz = horizons.compute(np.array([x0]), np.array([y0]), np.array([lon]), d, CFG)[0]
    k = int(np.argmax(hz))
    assert abs(k * 2 - 90) <= 30 and hz.max() > 5


def test_quantize_roundtrip_range():
    m = np.array([-3.0, 0.0, 1.234, 37.8, 50.0, -10.0])
    q = horizons.quantize(m)
    back = horizons.dequantize(q)
    assert np.all(np.abs(back[:4] - m[:4]) <= 0.081) and q[4] == 255 and q[5] == 0
