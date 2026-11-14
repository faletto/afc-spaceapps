"""South Pole tier build (spec §3.5-3.8): cell horizons + visibility, best cell per plot, PSR/ice, plot table.

Stage 1 (`build_cells`, ~15 min, cached to data/work/polar_cells.npz): for every 240 m cell in a plot inside the
85 deg S disc compute the terrain horizon (kept quantised), annual statistics and sub-scores.
Stage 2 (`build_plots`): pick the best cell per plot, recompute its full statistics (monthly, best windows), ice
distance, land type, price.
"""
import time
from pathlib import Path

import numpy as np

from . import ephemeris, horizons, land, polar, terrain, visibility

HALF_M = terrain.POLAR_HALF_M
CELL_M, PLOT_M = 240.0, 960.0
NC, NP = 1280, 320
K = round(PLOT_M / CELL_M)  # cells per plot side
HZ_UNIT, HZ_OFFSET = 0.16, -6.0  # quantisation (spec: -3; real skylines reach -5.8 deg)


def plot_in_disc():
    """(NP, NP) bool: plot centre at lat <= lat_min (85 deg S)."""
    px, py = polar.cell_centers(NP, PLOT_M, HALF_M)
    return polar.xy_to_lonlat(px, py)[0] <= -85.0


def cell_index_of_plots():
    """Flat cell indices (row*NC+col) grouped per plot: array (n_plots_in_disc, 16), plus plot (row, col)."""
    pr, pc = np.nonzero(plot_in_disc())
    dr, dc = np.divmod(np.arange(K * K), K)
    rows = pr[:, None] * K + dr[None]
    cols = pc[:, None] * K + dc[None]
    return rows * NC + cols, pr, pc


def build_cells(cfg, raw_dir, work_dir, chunk=60_000, log=print) -> Path:
    work = Path(work_dir)
    out = work / "polar_cells.npz"
    flat, pr, pc = cell_index_of_plots()
    idx = flat.ravel()
    cx, cy = polar.cell_centers(NC, CELL_M, HALF_M)
    x, y = cx.ravel()[idx].astype(float), cy.ravel()[idx].astype(float)
    lat, lon = polar.xy_to_lonlat(x, y)
    n = len(idx)
    cells = np.load(work / "terrain_polar_cells_20m.npz")
    cs = {k: cells[k].ravel()[idx] for k in cells.files}
    dems = horizons.load_dems(raw_dir)
    eph = ephemeris.load()
    lm = land.load_landmarks()
    hzq = np.empty((n, 180), np.uint8)
    stats = {k: np.empty(n) for k in visibility.KEYS}
    lscore = np.empty(n)
    t0 = time.time()
    for a in range(0, n, chunk):
        s = slice(a, min(a + chunk, n))
        hz = horizons.compute(x[s], y[s], lon[s], dems, cfg)
        q = horizons.quantize(hz, HZ_UNIT, HZ_OFFSET)
        hzq[s] = q
        st = visibility.site_stats(lat[s], lon[s], hz.astype(np.float64), eph, cfg)
        for k in visibility.KEYS:
            stats[k][s] = st[k]
        lscore[s], _ = land.landmark_score_and_nearby(lat[s], lon[s], lm, cfg, chunk=2000)
        log(f"cells {s.stop}/{n}  {time.time() - t0:.0f}s")
    np.savez(out, idx=idx, x=x, y=y, lat=lat, lon=lon, hzq=hzq, landmark_score=lscore,
             **{f"cs_{k}": v for k, v in cs.items()}, **stats)
    return out
