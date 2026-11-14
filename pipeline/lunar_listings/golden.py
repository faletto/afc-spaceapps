"""Golden vectors v1: reference outputs the TypeScript mirror must reproduce (tolerances stored alongside)."""
import json
from pathlib import Path

import numpy as np

from . import config, contract, ephemeris, geometry, horizons, pricing, scoring, visibility

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
            "horizon_quantisation": {"unit_deg": contract.HZ_UNIT_DEG, "offset_deg": contract.HZ_OFFSET_DEG,
                                     "cases": [{"deg": float(m), "q": int(horizons.quantize(np.array([m]))[0])} for m in (-7.0, -6.0, -2.5, 0.0, 1.234, 12.5, 34.8, 40.0)]}}


def write() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "golden_v1.json"
    p.write_text(json.dumps(build(), indent=1))
    return p


def _site(sid, lat, lon, hz, hazard, lscore, safe, prem, ice):
    return {"id": sid, "lat": float(lat), "lon": float(lon), "horizon_deg": [round(float(x), 4) for x in hz],
            "hazard_score": float(hazard), "landmark_score": float(lscore), "landing_safe": bool(safe),
            "premium": float(prem), "ice_km": None if ice is None else float(ice)}


def build_rent(work_dir=None, allow_partial: bool = False) -> dict:
    """Rent golden vectors: site inputs are embedded so the file is self-contained for the TS mirror."""
    from . import horizons, polar, pricing

    cfg, eph = config.load(), ephemeris.load()
    cj = Path(__file__).resolve().parents[2] / "app" / "public" / "data" / "config.json"
    cutoff = round(json.loads(cj.read_text())["computed"]["scarcity_viability_cutoff"], 4)  # the exported value
    sites = [_site("eq", 0.0, 0.0, np.zeros(180), 0.2, 0.1, True, 0.0, None),
             _site("midlat", 45.0, 100.0, np.zeros(180), 0.35, 0.3, True, 0.0, None),
             _site("farside", 0.0, 180.0, np.zeros(180), 0.25, 0.05, True, 0.0, None)]
    npz = Path(work_dir or Path(__file__).resolve().parents[2] / "data" / "work") / "polar_plots.npz"
    if not npz.exists() and not allow_partial:
        raise FileNotFoundError(f"{npz} missing: run `make polar` first (or pass allow_partial=True for a reduced golden set)")
    if npz.exists():
        o = np.load(npz)
        la, lo = polar.xy_to_lonlat(o["best_x"], o["best_y"])
        for sid, i in (("SP-0032-0154", int(np.flatnonzero((o["plot_row"] == 32) & (o["plot_col"] == 154))[0])),
                       ("SP-0172-0148", int(np.flatnonzero((o["plot_row"] == 172) & (o["plot_col"] == 148))[0])),
                       ("top_viability", int(np.argmax(o["viability"]))), ("psr", int(np.argmin(o["sunlit_frac"])))):
            sites.append(_site(sid, la[i], lo[i], horizons.dequantize(o["hzq"][i]), o["hazard_score"][i],
                               o["landmark_score"][i], o["landing_safe"][i], 0.0, o["ice_km"][i]))
    cases = []
    for s in sites:
        for day in (1, 100, 218, 232, 274, 288, 330, 366):
            for stay in (14, 30, 90, 366):
                r = pricing.rent_for_stay(s, eph, cfg, cutoff, day, stay)
                cases.append({"site": s["id"], "move_in_day": day, "stay_days": stay, **{k: float(v) for k, v in r.items()}})
    return {"version": 1, "scarcity_cutoff": cutoff, "tolerances": {"rel": 1e-9}, "sites": sites, "cases": cases}


def write_rent() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "golden_rent_v1.json"
    p.write_text(json.dumps(build_rent(), separators=(",", ":")))
    return p
