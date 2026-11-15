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


def global_plot_stats(
    dem: np.ndarray, slope: np.ndarray, max_slope_deg: float, n: int = CELLS_PER_DEG
) -> dict:
    """Per-block stats; blocks are n x n source pixels (n=32 for 1-deg global plots)."""
    z, s = plot_blocks(dem, n), plot_blocks(slope, n)
    return {
        "slope_mean_deg": np.nanmean(s, -1),
        "slope_p90_deg": np.nanpercentile(s, 90, axis=-1),
        "safe_area_frac": np.nanmean(np.where(np.isnan(s), np.nan, s < max_slope_deg), -1),
        "roughness_m": detrended_std(z, n),
        "relief_m": z.max(-1) - z.min(-1),
    }


def norm(x, lo_hi):
    lo, hi = lo_hi
    return np.clip((np.asarray(x) - lo) / (hi - lo), 0, 1)


def hazard_score(p90, rough, relief, cfg) -> np.ndarray:
    """Mean of normalised slope_p90, roughness, relief (0 = benign, 1 = hazardous)."""
    sf = cfg["safety"]
    return (
        norm(p90, sf["slope_p90_range"])
        + norm(rough, sf["roughness_range_m"])
        + norm(relief, sf["relief_range_m"])
    ) / 3


def resample_global(tif, out_npy, strip_rows: int = 2048) -> np.ndarray:
    """Block-mean the LOLA global DEM (int16, scale 0.5 m/DN) to 1/32 deg, strip by strip. Writes float32 metres."""
    import rasterio

    with rasterio.open(tif) as ds:
        h, w = ds.shape
        scale = ds.scales[0] if ds.scales else 1.0
        f = h // (180 * CELLS_PER_DEG)  # source pixels per output cell
        assert h % f == 0 and w % f == 0 and strip_rows % f == 0
        out = np.empty((h // f, w // f), np.float32)
        for r0 in range(0, h, strip_rows):
            a = ds.read(1, window=((r0, min(r0 + strip_rows, h)), (0, w)))
            out[r0 // f : (r0 + a.shape[0]) // f] = (
                resample_block_mean(a, (a.shape[0] // f, w // f), nodata=ds.nodata) * scale
            )
    np.save(out_npy, out)
    return out


def build_global_stats(dem_npy, out_npz, max_slope_deg: float) -> dict:
    dem = np.load(dem_npy)
    st = global_plot_stats(dem, slope_deg_lonlat(dem), max_slope_deg)
    np.savez_compressed(out_npz, **{k: v.astype(np.float32) for k, v in st.items()})
    return st


# ---------------------------------------------------------------- polar tier (south polar stereographic)
POLAR_HALF_M = 153_600.0  # core square half-width: 320 x 320 plots of 960 m (n_plots=320); covers the 85 deg S disc (r = 151.8 km)


def read_polar_core(tif, half_m: float = POLAR_HALF_M):
    """Read the central square of a PGDA polar GeoTIFF. Returns (array float32 metres, res_m).

    Transform is read from the header and asserted: square pixels, pole at the raster centre.
    Stereographic scale distortion at 85 deg S is ~0.2% (ignored; documented in spec 3.4).
    """
    import rasterio
    from rasterio.windows import from_bounds

    with rasterio.open(tif) as ds:
        res = ds.res[0]
        assert abs(ds.res[0] - ds.res[1]) < 1e-6
        b = ds.bounds
        assert abs(b.left + b.right) < 1 and abs(b.top + b.bottom) < 1, "pole not at raster centre"
        win = from_bounds(-half_m, -half_m, half_m, half_m, ds.transform).round_offsets().round_lengths()
        a = ds.read(1, window=win).astype(np.float32)
        if ds.nodata is not None:
            a[a == ds.nodata] = np.nan
    return a, res


def slope_deg_planar(dem: np.ndarray, res_m: float) -> np.ndarray:
    gy, gx = np.gradient(dem, res_m)
    return np.degrees(np.arctan(np.hypot(gx, gy))).astype(np.float32)


def polar_block_stats(dem, slope, res_m, block_m, max_slope_deg, rows_per_chunk=8):
    """Stats per block_m x block_m block (e.g. 240 m cells, 960 m plots), chunked over block rows."""
    n = round(block_m / res_m)
    nb = dem.shape[0] // n
    out = {}
    for r0 in range(0, nb, rows_per_chunk):
        sl = slice(r0 * n, min(r0 + rows_per_chunk, nb) * n)
        part = global_plot_stats(dem[sl], slope[sl], max_slope_deg, n)
        part["elev_mean_m"] = plot_blocks(dem[sl], n).mean(-1)
        for k, v in part.items():
            out.setdefault(k, []).append(v)
    return {k: np.concatenate(v, axis=0) for k, v in out.items()}


def polar_plot_centers(n_plots: int, plot_m: float):
    """x, y (metres, +y up) of plot centres for an n x n plot grid centred on the pole; row 0 at +y."""
    c = (np.arange(n_plots) + 0.5 - n_plots / 2) * plot_m
    x = np.broadcast_to(c[None, :], (n_plots, n_plots))
    y = np.broadcast_to(-c[:, None], (n_plots, n_plots))
    return x, y


def polar_lat_deg(x, y):
    """South polar stereographic (k0=1 at pole): lat from radius, r = 2R tan((90-|lat|)/2)."""
    r = np.hypot(x, y)
    return -90.0 + np.degrees(2 * np.arctan(r / (2 * R_M)))


LDSM_NAME, LDSM_BYTES = "LDSM_80S_20MPP_ADJ.TIF", 3_778_056_355


def polar_slope(raw_dir, dem, res) -> tuple[np.ndarray, str]:
    """Slope (deg) on the polar core grid: NASA's LDSM 20 m slope product when fully downloaded (spec §3.4),
    otherwise our own central differences on the DEM (same grid, same units)."""
    from pathlib import Path

    f = Path(raw_dir) / LDSM_NAME
    if res == 20.0 and f.exists() and f.stat().st_size == LDSM_BYTES:
        s, r2 = read_polar_core(f)
        assert r2 == res and s.shape == dem.shape, "LDSM grid does not match the DEM"
        return s, f"{LDSM_NAME} (NASA PGDA)"
    return slope_deg_planar(dem, res), "own central differences on the DEM"


def build_polar_stats(raw_dir, out_dir, cfg) -> str:
    """Polar cell (cell_m) and plot (plot_m) stats. Uses the 20 m DEM and LDSM slope if fully downloaded, else the
    80 m DEM and our own slope. Writes terrain_polar_source.json recording what was used."""
    import json
    from pathlib import Path

    raw, out_dir = Path(raw_dir), Path(out_dir)
    name, full = "LDEM_80S_20MPP_ADJ.TIF", 2_696_082_051
    f20 = raw / name
    src = f20 if f20.exists() and f20.stat().st_size == full else raw / "LDEM_80S_80MPP_ADJ.TIF"
    dem, res = read_polar_core(src)
    slope, slope_src = polar_slope(raw, dem, res)
    p = cfg["grid"]["polar"]
    ms = cfg["safety"]["max_slope_deg"]
    cells = polar_block_stats(dem, slope, res, p["cell_m"], ms)
    plots = polar_block_stats(dem, slope, res, p["plot_m"], ms)
    tag = f"{round(res)}m"
    np.savez_compressed(out_dir / f"terrain_polar_cells_{tag}.npz", **cells)
    np.savez_compressed(out_dir / f"terrain_polar_plots_{tag}.npz", **plots)
    (out_dir / "terrain_polar_source.json").write_text(
        json.dumps({"dem": src.name, "slope": slope_src, "res_m": res})
    )
    return f"{src.name} + slope: {slope_src}"
