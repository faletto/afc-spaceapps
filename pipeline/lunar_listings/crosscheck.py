"""Independent NASA cross-checks of the polar tier (HOR-2 spirit, TEMP-4).

* LOLA-derived average Sun / Earth visibility maps (PGDA `AVGVISIB_85S_060M`, `..._EARTH`, `LPSR`; Mazarico et al.):
  compared with our terrain-horizon lighting (`sunlit_frac`, `earth_frac`) at each plot's best cell.
* LRO Diviner polar cumulative products (PDS `urn:nasa:pds:lro_diviner_derived1:data_derived_pcp`, 240 m bins,
  average bolometric brightness temperature by local time): compared with our T1 temperatures.
Same projection and axes as ours (verified: Diviner x,y normalised by R reproduce clon/clat via polar.xy_to_lonlat).
"""
from pathlib import Path

import numpy as np

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
R = 1_737_400.0


def _read_illum(name):
    import rasterio

    with rasterio.open(RAW / "illum" / f"{name}.TIF") as ds:
        a = ds.read(1).astype(np.float32)
        a = np.where(a == ds.nodata, np.nan, a * ds.scales[0] + ds.offsets[0])
        return a, ds.bounds.left, ds.bounds.top, ds.res[0]


def sample_illum(name, x, y, window_m=240.0):
    """Mean of the map over a square window (our cell size) centred on (x, y), ignoring NaNs."""
    a, left, top, res = _read_illum(name)
    h = max(1, round(window_m / res / 2))
    c = np.round((x - left) / res - 0.5).astype(int)
    r = np.round((top - y) / res - 0.5).astype(int)
    out = np.full(len(x), np.nan)
    ok = (c >= h) & (r >= h) & (c < a.shape[1] - h) & (r < a.shape[0] - h)
    for i in np.flatnonzero(ok):
        out[i] = np.nanmean(a[r[i] - h : r[i] + h + 1, c[i] - h : c[i] + h + 1])
    return out


def sample_diviner(fname, x, y):
    """Diviner Tbol (K) of the nearest 240 m bin, NaN if none within 0.6 bin."""
    import pandas as pd

    d = pd.read_csv(RAW / "diviner" / fname, sep=",", skiprows=1, header=None, names=["x", "y", "clon", "clat", "tbol"],
                    skipinitialspace=True)
    xm, ym = d.x.to_numpy() * R, d.y.to_numpy() * R
    step = float(np.median(np.diff(np.sort(np.unique(xm)))))
    x0, y0 = xm.min(), ym.min()
    nx, ny = int(round((xm.max() - x0) / step)) + 1, int(round((ym.max() - y0) / step)) + 1
    grid = np.full((ny, nx), np.nan, np.float32)
    grid[np.round((ym - y0) / step).astype(int), np.round((xm - x0) / step).astype(int)] = d.tbol.to_numpy()
    ix, iy = np.round((x - x0) / step).astype(int), np.round((y - y0) / step).astype(int)
    out = np.full(len(x), np.nan)
    ok = (ix >= 0) & (iy >= 0) & (ix < nx) & (iy < ny)
    out[ok] = grid[iy[ok], ix[ok]]
    return out


def stats(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    a, b = a[m], b[m]
    return {"n": int(m.sum()), "r": float(np.corrcoef(a, b)[0, 1]), "bias": float(np.mean(a - b)),
            "rmse": float(np.sqrt(np.mean((a - b) ** 2))), "within": float(np.mean(np.abs(a - b) <= 0.1))}


def run(plots_npz) -> dict:
    o = np.load(plots_npz)
    x, y = o["best_x"].astype(float), o["best_y"].astype(float)
    res = {}
    sun = sample_illum("AVGVISIB_85S_060M_201608", x, y)
    earth = sample_illum("AVGVISIB_85S_060M_201608_EARTH", x, y)
    res["sun"] = stats(o["sunlit_frac"], sun)
    res["earth"] = stats(o["earth_frac"], earth)
    psr_lola = sun < 0.01
    psr_ours = o["sunlit_frac"] < 0.01
    ok = np.isfinite(sun)
    res["psr"] = {"ours_pct": float(100 * psr_ours[ok].mean()), "lola_pct": float(100 * psr_lola[ok].mean()),
                  "agree_pct": float(100 * (psr_ours == psr_lola)[ok].mean())}
    res["_arrays"] = {"sun_ours": o["sunlit_frac"], "sun_lola": sun, "earth_ours": o["earth_frac"], "earth_lola": earth}
    d = "pcp_avg_tbol_pols_{}_240.tab"
    tmax = np.fmax(sample_diviner(d.format("sum_ltim12"), x, y), sample_diviner(d.format("win_ltim12"), x, y))
    tnight = np.fmin(sample_diviner(d.format("sum_ltim03"), x, y), sample_diviner(d.format("win_ltim03"), x, y))
    res["tmax"] = {**stats(o["temp_max_k"], tmax), "bias_k": float(np.nanmean(o["temp_max_k"] - tmax)),
                   "rmse_k": float(np.sqrt(np.nanmean((o["temp_max_k"] - tmax) ** 2)))}
    lit = o["sunlit_frac"] > 0.3
    res["tnight"] = {"n": int((lit & np.isfinite(tnight)).sum()), "ours_floor_k": float(np.median(o["temp_min_k"][lit])),
                     "diviner_median_k": float(np.nanmedian(tnight[lit])), "diviner_p10_k": float(np.nanpercentile(tnight[lit], 10))}
    psr_m = psr_ours & np.isfinite(tmax)
    res["psr_t"] = {"n": int(psr_m.sum()), "ours_k": float(np.median(o["temp_max_k"][psr_m])), "diviner_median_k": float(np.nanmedian(tmax[psr_m])),
                    "diviner_p90_k": float(np.nanpercentile(tmax[psr_m], 90))}
    res["_arrays"].update(tmax_ours=o["temp_max_k"], tmax_div=tmax)
    return res


def markdown(res) -> list[str]:
    s, e, p, t, n, pt = res["sun"], res["earth"], res["psr"], res["tmax"], res["tnight"], res["psr_t"]
    return [
        "", "## Independent cross-checks of the South Pole tier (NASA data)", "",
        "### Lighting vs LOLA-derived average visibility (PGDA, Mazarico et al.; HOR-2 cross-check)",
        f"Our `sunlit_frac`/`earth_frac` at each plot's best cell vs the LOLA 60 m maps averaged over our 240 m cell "
        f"({s['n']:,} plots).", "",
        "| Quantity | Pearson r | bias (ours − LOLA) | RMSE | within ±0.10 |", "|---|---|---|---|---|",
        f"| Sun visible fraction | {s['r']:.3f} | {s['bias']:+.3f} | {s['rmse']:.3f} | {100 * s['within']:.0f}% |",
        f"| Earth visible fraction | {e['r']:.3f} | {e['bias']:+.3f} | {e['rmse']:.3f} | {100 * e['within']:.0f}% |", "",
        f"PSR (< 1% sunlit): ours {p['ours_pct']:.1f}% of plots, LOLA {p['lola_pct']:.1f}%, classification agrees on {p['agree_pct']:.1f}%.",
        "Expected differences: our `sunlit` counts the Sun only when more than half of its disk is above the terrain "
        "(LOLA counts any illumination, so it reads higher); our Earth contact needs 1° above the horizon and covers only 2028 "
        "(LOLA integrates 2016-2020 libration); LOLA's grid is 60 m vs our 240 m cell mean.", "",
        "### Temperature vs LRO Diviner polar maps (TEMP-4)",
        "Diviner average bolometric brightness temperature in 240 m bins by local time (PDS `lro_diviner_derived1`, "
        "summer and winter seasons). Our T1 is an equilibrium model with floors (95 K sunlit, 40 K PSR).", "",
        "| Comparison | n | Result |", "|---|---|---|",
        f"| Max temperature (ours annual max vs Diviner max of local-noon bins) | {t['n']:,} | r = {t['r']:.2f}, bias {t['bias_k']:+.0f} K, RMSE {t['rmse_k']:.0f} K |",
        f"| Night floor at lit sites (>30% sunlit) | {n['n']:,} | ours {n['ours_floor_k']:.0f} K vs Diviner median {n['diviner_median_k']:.0f} K (10th pct {n['diviner_p10_k']:.0f} K) |",
        f"| PSR plots, max temperature | {pt['n']:,} | ours {pt['ours_k']:.0f} K vs Diviner median {pt['diviner_median_k']:.0f} K (90th pct {pt['diviner_p90_k']:.0f} K) |", "",
        "**Reading:** permanently shadowed plots agree (40 K floor vs Diviner ≈ 43 K). For sunlit sites our modelled annual "
        f"maximum (flat surface at peak Sun elevation) is far above Diviner's local-time-binned averages (bias {t['bias_k']:+.0f} K, r = {t['r']:.2f}), because "
        "the binned maps average over season, sun angle and sub-bin shadowing and so do not capture annual extremes, while T1 ignores "
        "terrain-scattered light and subsurface conduction. TEMP-4 is therefore a coarse check: shadowed terrain validates, lit-site "
        "maxima and the 95 K night floor (Diviner nights ≈ 65 K) are conservative/modelled values and the app labels temperatures as "
        "modelled. The thermal sub-score uses the swing (max − min), so it likely overstates polar swings (Q-P8).", "",
    ]
