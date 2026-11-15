"""Terrain horizons (spec §3.5, HOR-1): elevation angle of the terrain skyline vs azimuth, with lunar curvature.

Two-resolution DEM: `near` (20 m, cropped around the core) within `near_dem_radius_m`, `far` (80 m, full +-304 km)
beyond. Rasters are centred on the pole: pixel (r, c) centre at x = -half + (c+0.5)*res, y = +half - (r+0.5)*res.
Azimuth k is bearing k * 360/naz from local north (see polar.py): the ray runs along map angle lon + bearing.
"""

from dataclasses import dataclass

import numpy as np
from numba import njit, prange

from .contract import HZ_OFFSET_DEG, HZ_UNIT_DEG

R_M = 1_737_400.0


@dataclass
class Dems:
    near: np.ndarray
    near_half_m: float
    near_res_m: float
    far: np.ndarray
    far_half_m: float
    far_res_m: float


@njit(cache=True, inline="always")
def _sample(dem, half, res, x, y):
    """Bilinear sample; NaN outside the raster or if any corner is NaN."""
    fc = (x + half) / res - 0.5
    fr = (half - y) / res - 0.5
    n = dem.shape[0]
    if fc < 0 or fr < 0 or fc >= n - 1 or fr >= n - 1:
        return np.nan
    c0, r0 = int(fc), int(fr)
    tc, tr = fc - c0, fr - r0
    return (dem[r0, c0] * (1 - tc) + dem[r0, c0 + 1] * tc) * (1 - tr) + (
        dem[r0 + 1, c0] * (1 - tc) + dem[r0 + 1, c0 + 1] * tc
    ) * tr


@njit(cache=True, parallel=True)
def _kernel(
    xs, ys, lons, near, nhalf, nres, far, fhalf, fres, naz, d_min, d_max, growth, mast, near_r, R, out
):
    n = xs.shape[0]
    step = 360.0 / naz
    for i in prange(n):
        h0 = _sample(near, nhalf, nres, xs[i], ys[i])
        if np.isnan(h0):
            h0 = _sample(far, fhalf, fres, xs[i], ys[i])
        if np.isnan(h0):
            for k in range(naz):
                out[i, k] = np.nan
            continue
        h0 += mast
        for k in range(naz):
            a = np.radians(lons[i] + k * step)
            dx, dy = np.sin(a), np.cos(a)
            best = -1e9
            d = d_min
            while d <= d_max:
                x, y = xs[i] + d * dx, ys[i] + d * dy
                h = np.nan
                if d <= near_r:
                    h = _sample(near, nhalf, nres, x, y)
                if np.isnan(h):
                    h = _sample(far, fhalf, fres, x, y)
                    if np.isnan(h) and (abs(x) >= fhalf or abs(y) >= fhalf):
                        break  # left the data
                if not np.isnan(h):
                    ang = np.arctan2(h - d * d / (2.0 * R) - h0, d)
                    best = max(best, ang)
                d *= 1.0 + growth
            out[i, k] = np.degrees(best) if best > -1e8 else np.nan


def compute(xs, ys, lons, dems: Dems, cfg: dict, R=R_M) -> np.ndarray:
    """Horizon elevation angles (deg), float32, shape (n, naz)."""
    hz = cfg["horizon"]
    naz = round(360 / hz["az_step_deg"])
    out = np.empty((len(xs), naz), np.float32)
    _kernel(
        np.ascontiguousarray(xs, float),
        np.ascontiguousarray(ys, float),
        np.ascontiguousarray(lons, float),
        dems.near,
        dems.near_half_m,
        dems.near_res_m,
        dems.far,
        dems.far_half_m,
        dems.far_res_m,
        naz,
        cfg["grid"]["polar"]["cell_m"] / 2.0,
        hz["d_max_m"],
        hz["step_growth"],
        hz["mast_m"],
        hz["near_dem_radius_m"],
        R,
        out,
    )
    return out


def compute_ref(x, y, lon, dems: Dems, cfg: dict, R=R_M, ray_step_m=None) -> np.ndarray:
    """Pure-Python reference for ONE cell. With `ray_step_m` it samples uniformly (independent of the geometric
    schedule) so tests can check the optimised kernel against a dense brute-force skyline."""
    from scipy.ndimage import map_coordinates

    hz = cfg["horizon"]
    naz = round(360 / hz["az_step_deg"])

    def samp(dem, half, res, xx, yy):
        fc, fr = (xx + half) / res - 0.5, (half - yy) / res - 0.5
        ok = (fc >= 0) & (fr >= 0) & (fc < dem.shape[0] - 1) & (fr < dem.shape[0] - 1)
        v = map_coordinates(dem, [np.where(ok, fr, 0), np.where(ok, fc, 0)], order=1)
        return np.where(ok, v, np.nan)

    def height(xx, yy, d):
        h = np.where(
            d <= hz["near_dem_radius_m"], samp(dems.near, dems.near_half_m, dems.near_res_m, xx, yy), np.nan
        )
        return np.where(np.isnan(h), samp(dems.far, dems.far_half_m, dems.far_res_m, xx, yy), h)

    h0 = float(height(np.array([x]), np.array([y]), np.array([0.0]))[0]) + hz["mast_m"]
    if ray_step_m:
        d = np.arange(ray_step_m, hz["d_max_m"] + 1e-9, ray_step_m)
    else:
        n = int(
            np.floor(
                np.log(hz["d_max_m"] / (cfg["grid"]["polar"]["cell_m"] / 2)) / np.log(1 + hz["step_growth"])
            )
        )
        d = cfg["grid"]["polar"]["cell_m"] / 2 * (1 + hz["step_growth"]) ** np.arange(n + 1)
    out = np.empty(naz)
    for k in range(naz):
        a = np.radians(lon + k * 360.0 / naz)
        h = height(x + d * np.sin(a), y + d * np.cos(a), d)
        ang = np.arctan2(h - d * d / (2 * R) - h0, d)
        out[k] = np.degrees(np.nanmax(ang)) if np.isfinite(ang).any() else np.nan
    return out


def quantize(m_deg: np.ndarray, unit=HZ_UNIT_DEG, offset=HZ_OFFSET_DEG) -> np.ndarray:
    """uint8 = round((m - offset)/unit); contract: unit 0.16, offset -6 -> -6..+34.8 deg (spec said -3; real skylines reach -5.8)."""
    m = np.nan_to_num(np.asarray(m_deg, float), nan=offset, posinf=1e9, neginf=-1e9)  # NaN -> minimum code
    return np.clip(np.rint((m - offset) / unit), 0, 255).astype(np.uint8)


def dequantize(q: np.ndarray, unit=HZ_UNIT_DEG, offset=HZ_OFFSET_DEG) -> np.ndarray:
    return q.astype(np.float32) * unit + offset


def load_dems(raw_dir, near_half_m: float = 160_000.0) -> Dems:
    """Real PGDA DEMs: 20 m cropped to +-near_half_m and the full 80 m raster (NaN = no data)."""
    from pathlib import Path

    from . import terrain

    raw = Path(raw_dir)
    near, _ = terrain.read_polar_core(raw / "LDEM_80S_20MPP_ADJ.TIF", half_m=near_half_m)
    far, _ = terrain.read_polar_core(raw / "LDEM_80S_80MPP_ADJ.TIF", half_m=304_000.0)
    return Dems(near, near_half_m, 20.0, far, 304_000.0, 80.0)
