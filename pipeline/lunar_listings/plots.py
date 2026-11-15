"""Plot tables. Global tier: 180 x 360 plots of 1 deg, ordered lat index from the SOUTH (row 0 = 90S..89S), lon from -180."""

from pathlib import Path

import numpy as np

from . import ephemeris, land, pricing, scoring, terrain, visibility

R_M = 1_737_400.0


def global_geometry():
    lat_idx = np.repeat(np.arange(180), 360)
    lon_idx = np.tile(np.arange(360), 180)
    lat, lon = lat_idx - 89.5, lon_idx - 179.5
    area = R_M**2 * np.radians(1.0) * (np.sin(np.radians(lat + 0.5)) - np.sin(np.radians(lat - 0.5))) / 1e6
    return {"lat_idx": lat_idx, "lon_idx": lon_idx, "lat": lat, "lon": lon, "area_km2": area}


def build_global(cfg, work_dir) -> dict:
    """Terrain (data/work/terrain_global.npz, north-first) + visibility -> one flat table (south-first)."""
    work = Path(work_dir)
    t = np.load(work / "terrain_global.npz")
    g = global_geometry()
    tab = dict(g)
    for k in t.files:
        tab[k] = np.flipud(t[k]).ravel().astype(np.float32)
    sf = cfg["safety"]
    tab["landing_safe"] = tab["safe_area_frac"] >= sf["min_safe_frac"]
    tab["hazard_score"] = terrain.hazard_score(tab["slope_p90_deg"], tab["roughness_m"], tab["relief_m"], cfg)
    vis = visibility.site_stats(g["lat"], g["lon"], np.zeros((g["lat"].size, 180)), ephemeris.load(), cfg)
    tab.update(vis)
    dem = np.load(work / "dem_global_32.npy")
    tab["elev_mean_m"] = np.flipud(terrain.plot_blocks(dem).mean(-1)).ravel()
    hi, lo = land.plot_tpi_extremes(dem, cfg["land"]["tpi_radius_km"])
    tab["tpi_p90_m"], tab["tpi_p10_m"] = np.flipud(hi).ravel(), np.flipud(lo).ravel()
    lm = land.load_landmarks()
    tab["landmark_score"], tab["nearby"] = land.landmark_score_and_nearby(g["lat"], g["lon"], lm, cfg)
    tab["land_type"] = land.land_type(
        tab["sunlit_frac"],
        g["lat"],
        g["lon"],
        tab["elev_mean_m"],
        tab["tpi_p90_m"],
        tab["tpi_p10_m"],
        cfg,
        polar=False,
    )
    eph = ephemeris.load()
    sunlit, eok = visibility.site_masks(g["lat"], g["lon"], np.zeros((g["lat"].size, 180)), eph, cfg)
    ht = cfg["home_types"]
    tab["bw_lander_h"], tab["bw_lander_start"] = visibility.best_window(
        sunlit, ht["lander_pad"]["ref_stay_days"]
    )
    tab["bw_habitat_h"], tab["bw_habitat_start"] = visibility.best_window(eok, ht["habitat"]["ref_stay_days"])
    del sunlit, eok
    th = scoring.thermal_hazard(tab["temp_min_k"], tab["temp_max_k"], cfg)
    tab["thermal_hazard_score"] = th
    s = scoring.subscores(tab, cfg)
    tab.update({f"s_{k}": v for k, v in s.items()})
    tab["viability"] = scoring.viability(s, tab["landing_safe"], cfg)
    cut = pricing.scarcity_cutoff(tab["viability"], cfg)
    tab["scarcity_cutoff"] = np.float64(cut)
    tab["apollo_km"] = land.apollo_distance_km(g["lat"], g["lon"], lm)
    prem = pricing.landmark_premium(tab["apollo_km"], tab["land_type"] == land.LT["peak_of_light"], cfg)
    tab["price"] = pricing.price_usd(tab["viability"], cfg, prem, cut)
    tab["rent_avg"] = pricing.rent_per_month(tab["price"], cfg)
    np.savez_compressed(work / "plots_global.npz", **tab)
    return tab
