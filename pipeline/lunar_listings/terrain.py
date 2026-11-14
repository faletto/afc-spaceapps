"""Terrain: global resample, slope, per-plot statistics (spec §3.4).

Global arrays are indexed [row, col] with row 0 = +90 (north), col 0 = -180 (west); cell size 1/32 deg.
"""
import numpy as np

R_M = 1_737_400.0
CELLS_PER_DEG = 32


def lat_centers(n_rows: int) -> np.ndarray:
    """Latitude of each row centre, degrees (north first)."""
    step = 180.0 / n_rows
    return 90.0 - step * (np.arange(n_rows) + 0.5)


def resample_block_mean(src, out_shape, nodata=None):
    """Block-mean a 2-D array whose shape is an integer multiple of out_shape. NaN-aware."""
    fy, fx = src.shape[0] // out_shape[0], src.shape[1] // out_shape[1]
    a = src[: out_shape[0] * fy, : out_shape[1] * fx].astype(np.float32)
    if nodata is not None:
        a[a == nodata] = np.nan
    return np.nanmean(a.reshape(out_shape[0], fy, out_shape[1], fx), axis=(1, 3))


def slope_deg_lonlat(dem: np.ndarray, cell_deg: float = 1.0 / CELLS_PER_DEG) -> np.ndarray:
    """Slope (deg) by central differences; E-W spacing R*cos(lat)*dlon, clamped near the poles."""
    lat = np.radians(lat_centers(dem.shape[0]))
    dy = R_M * np.radians(cell_deg)
    dx = np.maximum(R_M * np.cos(lat) * np.radians(cell_deg), 0.05 * dy)[:, None]
    z = np.pad(dem, ((1, 1), (0, 0)), mode="edge")
    gy = (z[:-2] - z[2:]) / (2 * dy)  # north-positive gradient (rows run south)
    gx = (np.roll(dem, -1, axis=1) - np.roll(dem, 1, axis=1)) / (2 * dx)  # wraps in longitude
    return np.degrees(np.arctan(np.hypot(gx, gy))).astype(np.float32)


def plot_blocks(a: np.ndarray, n=CELLS_PER_DEG) -> np.ndarray:
    """(H, W) -> (H/n, W/n, n*n) block view per 1-degree plot."""
    h, w = a.shape
    return a.reshape(h // n, n, w // n, n).transpose(0, 2, 1, 3).reshape(h // n, w // n, n * n)


def detrended_std(z: np.ndarray, n=CELLS_PER_DEG) -> np.ndarray:
    """Std of elevation after removing a best-fit plane per block. z: (H/n, W/n, n*n)."""
    c = np.arange(n) - (n - 1) / 2
    X = np.tile(c, n)  # column coordinate (fast axis)
    Y = np.repeat(c, n)
    zc = z - z.mean(-1, keepdims=True)
    b = (zc * X).sum(-1, keepdims=True) / (X * X).sum()
    d = (zc * Y).sum(-1, keepdims=True) / (Y * Y).sum()
    return (zc - b * X - d * Y).std(-1)


def global_plot_stats(dem: np.ndarray, slope: np.ndarray, max_slope_deg: float) -> dict:
    z, s = plot_blocks(dem), plot_blocks(slope)
    return {
        "slope_mean_deg": s.mean(-1),
        "slope_p90_deg": np.percentile(s, 90, axis=-1),
        "safe_area_frac": (s < max_slope_deg).mean(-1),
        "roughness_m": detrended_std(z),
        "relief_m": z.max(-1) - z.min(-1),
    }


def norm(x, lo_hi):
    lo, hi = lo_hi
    return np.clip((np.asarray(x) - lo) / (hi - lo), 0, 1)


def hazard_score(p90, rough, relief, cfg) -> np.ndarray:
    """Mean of normalised slope_p90, roughness, relief (0 = benign, 1 = hazardous)."""
    sf = cfg["safety"]
    return (norm(p90, sf["slope_p90_range"]) + norm(rough, sf["roughness_range_m"])
            + norm(relief, sf["relief_range_m"])) / 3
