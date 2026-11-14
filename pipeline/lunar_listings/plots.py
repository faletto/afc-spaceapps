"""Plot tables. Global tier: 180 x 360 plots of 1 deg, ordered lat index from the SOUTH (row 0 = 90S..89S), lon from -180."""
from pathlib import Path

import numpy as np

from . import ephemeris, terrain, visibility

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
    np.savez_compressed(work / "plots_global.npz", **tab)
    return tab
