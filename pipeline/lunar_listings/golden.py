"""Golden vectors v1: reference outputs the TypeScript mirror must reproduce (tolerances stored alongside)."""
import json
from pathlib import Path

import numpy as np

from . import config, ephemeris, geometry, horizons, pricing, scoring, visibility

OUT = Path(__file__).resolve().parents[1] / "tests" / "golden"
SITES = [(0.0, 0.0), (30.0, 20.0), (-60.0, -150.0), (-85.0, -30.0), (-89.7, 45.0), (0.0, 180.0)]
HOURS = [0, 1000, 3333, 5000, 8000]


def build() -> dict:
    cfg, eph = config.load(), ephemeris.load()
    geo = []
    for lat, lon in SITES:
        for t in HOURS:
            se, sa = geometry.sun_az_el(eph["sun_xyz"][t], lat, lon)
            ee, ea = geometry.earth_az_el(eph["earth_xyz"][t], eph["earth_dist_m"][t], lat, lon)
            geo.append({"lat": lat, "lon": lon, "hour": t, "sun_el": float(se), "sun_az": float(sa),
                        "earth_el": float(ee), "earth_az": float(ea)})
    hz = np.zeros((len(SITES), 180))
    hz[4] = 1.5 + np.sin(np.radians(np.arange(180) * 6))  # a rugged polar horizon
    st = visibility.site_stats(np.array([s[0] for s in SITES]), np.array([s[1] for s in SITES]), hz, eph, cfg)
    sunlit, eok = visibility.site_masks(np.array([s[0] for s in SITES]), np.array([s[1] for s in SITES]), hz, eph, cfg)
    vis = []
    for i, (lat, lon) in enumerate(SITES):
        d = {k: float(st[k][i]) for k in visibility.KEYS}
        d.update(lat=lat, lon=lon, horizon=[float(x) for x in hz[i]],
                 monthly_sunlit=[float(x) for x in st["monthly_sunlit"][i]],
                 dark_runs=[list(map(int, r)) for r in visibility.runs_of_false(sunlit[i])],
                 blackout_runs=[list(map(int, r)) for r in visibility.runs_of_false(eok[i])],
                 best_window_lander=[int(v[i]) for v in visibility.best_window(sunlit, 14)],
                 best_window_habitat=[int(v[i]) for v in visibility.best_window(eok, 90)])
        vis.append(d)
    v = np.array([0, 25, 50, 75, 100.0])
    pr = [{"viability": float(x), "price": float(pricing.price_usd(x, cfg)),
           "price_scarce": float(pricing.price_usd(x, cfg, 0.25, cutoff=60)), "rent_month": float(pricing.rent_per_month(pricing.price_usd(x, cfg), cfg)),
           "formatted": pricing.format_usd(float(pricing.price_usd(x, cfg)))} for x in v]
    table = dict(hazard_score=0.3, energy_wh_m2_day=15000.0, longest_dark_h=200.0, earth_frac=0.8, longest_blackout_h=100.0,
                 temp_min_k=80.0, temp_max_k=300.0, landmark_score=0.4)
    sub = scoring.subscores({k: np.array([x]) for k, x in table.items()}, cfg)
    sc = {"input": table, "subscores": {k: float(a[0]) for k, a in sub.items()},
          "viability_safe": float(scoring.viability(sub, np.array([True]), cfg)[0]),
          "viability_unsafe": float(scoring.viability(sub, np.array([False]), cfg)[0])}
    return {"version": 1, "tolerances": {"angle_deg": 1e-6, "stat": 1e-9, "price_rel": 1e-9},
            "geometry": geo, "visibility": vis, "pricing": pr, "scoring": sc,
            "horizon_quantisation": {"unit_deg": 0.16, "offset_deg": -6.0,
                                     "cases": [{"deg": float(m), "q": int(horizons.quantize(np.array([m]))[0])} for m in (-7.0, -6.0, -2.5, 0.0, 1.234, 12.5, 34.8, 40.0)]}}


def write() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "golden_v1.json"
    p.write_text(json.dumps(build(), indent=1))
    return p
