"""South Pole tier build (spec §3.5-3.8): cell horizons + visibility, best cell per plot, PSR/ice, plot table.

Stage 1 (`build_cells`, ~15 min, cached to data/work/polar_cells.npz): for every 240 m cell in a plot inside the
85 deg S disc compute the terrain horizon (kept quantised), annual statistics and sub-scores.
Stage 2 (`build_plots`): pick the best cell per plot, recompute its full statistics (monthly, best windows), ice
distance, land type, price.
"""
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

from . import ephemeris, horizons, land, polar, scoring, terrain, visibility

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
    flat, _, _ = cell_index_of_plots()
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


def _cell_scores(c, cfg):
    """Cell sub-scores + viability from stage-1 stats and the 240 m terrain stats."""
    haz = terrain.hazard_score(c["cs_slope_p90_deg"], c["cs_roughness_m"], c["cs_relief_m"], cfg)
    t = {"hazard_score": haz, "energy_wh_m2_day": c["energy_wh_m2_day"], "longest_dark_h": c["longest_dark_h"],
         "earth_frac": c["earth_frac"], "longest_blackout_h": c["longest_blackout_h"], "temp_min_k": c["temp_min_k"],
         "temp_max_k": c["temp_max_k"], "landmark_score": c["landmark_score"]}
    s = scoring.subscores(t, cfg)
    safe = c["cs_safe_area_frac"] >= cfg["safety"]["min_safe_frac"]
    return s, safe, scoring.viability({k: v for k, v in s.items() if k != "ice"}, safe, cfg)


def build_plots(cfg, raw_dir, work_dir, log=print) -> dict:
    """Best cell per plot -> plot table (arrays over the n plots inside the disc, plot order = row-major)."""
    work = Path(work_dir)
    c = dict(np.load(work / "polar_cells.npz"))
    n_cells = len(c["idx"])
    n = n_cells // (K * K)
    _, safe, viab = _cell_scores(c, cfg)
    V = viab.reshape(n, K * K)
    Sf = safe.reshape(n, K * K)
    pick = np.argmax(np.where(Sf, V, -1.0), axis=1)  # best safe cell; if none safe, argmax of -1s -> cell 0 ...
    any_safe = Sf.any(1)
    pick = np.where(any_safe, pick, np.argmax(V, axis=1))
    sel = np.arange(n) * (K * K) + pick  # index into the cell arrays

    # PSR mask on the full cell grid (cells outside the disc = not PSR) and distance to the nearest PSR cell
    psr = np.zeros(NC * NC, bool)
    psr[c["idx"]] = c["sunlit_frac"] < 0.01
    dist_m = ndimage.distance_transform_edt(~psr.reshape(NC, NC), sampling=CELL_M)
    ice_km = dist_m.ravel()[c["idx"][sel]] / 1000.0

    # full statistics (monthly, run lists) for the best cells
    eph = ephemeris.load()
    hz = horizons.dequantize(c["hzq"][sel], HZ_UNIT, HZ_OFFSET).astype(np.float64)
    st = visibility.site_stats(c["lat"][sel], c["lon"][sel], hz, eph, cfg)
    sunlit, eok = visibility.site_masks(c["lat"][sel], c["lon"][sel], hz, eph, cfg)
    ht = cfg["home_types"]
    bwl = visibility.best_window(sunlit, ht["lander_pad"]["ref_stay_days"])
    bwh = visibility.best_window(eok, ht["habitat"]["ref_stay_days"])
    del sunlit, eok

    # plot-level area facts (whole plot) from the 960 m stats; plot grid -> plots in the disc
    pr, pc = np.nonzero(plot_in_disc())
    pl = np.load(work / "terrain_polar_plots_20m.npz")
    area = {k: pl[k][pr, pc] for k in pl.files}
    px, py = polar.cell_centers(NP, PLOT_M, HALF_M)
    plat, plon = polar.xy_to_lonlat(px[pr, pc], py[pr, pc])

    # plot-level sub-scores: safety from the whole plot, the rest from the best cell
    hazard = terrain.hazard_score(area["slope_p90_deg"], area["roughness_m"], area["relief_m"], cfg)
    cs = {k: c[k][sel] for k in ("energy_wh_m2_day", "longest_dark_h", "earth_frac", "longest_blackout_h",
                                  "temp_min_k", "temp_max_k", "landmark_score", "sunlit_frac")}
    lm = land.load_landmarks()
    plot_lscore, nearby = land.landmark_score_and_nearby(plat, plon, lm, cfg)
    cs["landmark_score"] = np.maximum(plot_lscore, cs["landmark_score"])
    tab = {**cs, "hazard_score": hazard, "ice_km": ice_km}
    sub = scoring.subscores(tab, cfg, polar=True)
    landing_safe = any_safe & (area["safe_area_frac"] >= cfg["safety"]["min_safe_frac"])
    viability = scoring.viability(sub, landing_safe, cfg)

    # land type: TPI from 240 m cell elevations over ~5 km, p90/p10 within the plot
    el = np.full(NC * NC, np.nan)
    el[c["idx"]] = c["cs_elev_mean_m"]
    el = np.where(np.isnan(el), np.nanmean(el), el).reshape(NC, NC)
    tpi = el - ndimage.uniform_filter(el, size=2 * round(cfg["land"]["tpi_radius_km"] * 1000 / CELL_M) + 1)
    tp = tpi.ravel()[c["idx"]].reshape(n, K * K)
    gdem = np.load(work / "dem_global_32.npy")
    gmed = float(np.median(terrain.plot_blocks(gdem).mean(-1)))  # global plot median (spec: mare = median - 1 km)
    ltype = land.land_type(cs["sunlit_frac"], plat, plon, area["elev_mean_m"], np.percentile(tp, 90, 1),
                           np.percentile(tp, 10, 1), cfg, polar=True, median_ref=gmed)
    apollo_km = land.apollo_distance_km(plat, plon, lm)
    out = {**{k: v for k, v in st.items()}, "plot_row": pr, "plot_col": pc, "lat": plat, "lon": plon,
           "x": px[pr, pc], "y": py[pr, pc], "area_km2": np.full(n, (PLOT_M / 1000) ** 2), "best_cell": c["idx"][sel],
           "best_x": c["x"][sel], "best_y": c["y"][sel], "hzq": c["hzq"][sel], "hazard_score": hazard,
           "landing_safe": landing_safe, "viability": viability, "land_type": ltype, "ice_km": ice_km,
           "landmark_score": cs["landmark_score"], "nearby": nearby, "apollo_km": apollo_km,
           "bw_lander_h": bwl[0], "bw_lander_start": bwl[1], "bw_habitat_h": bwh[0], "bw_habitat_start": bwh[1],
           **{f"s_{k}": v for k, v in sub.items()}, **{k: v for k, v in area.items()}}
    np.savez(work / "polar_plots.npz", **out)
    log(f"plots {n}  viability pct {np.round(np.percentile(viability, [0, 50, 99, 100]), 1)}")
    return out
