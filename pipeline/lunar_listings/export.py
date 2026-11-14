"""Real-data export in the contract formats (spec §3.11, §5). Global tier now; polar added in P4.

Only writes `<out>/global/**` and refreshes manifest.json; other tiers stay as they are (stub until P4).
"""
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

from . import CONTRACT_VERSION, land, stub

OVERLAY_FIELDS = {  # name -> (table field, lo, hi, unit)
    "viability": ("viability", 0, 100, "score"), "sunlit": ("sunlit_pct", 0, 100, "%"),
    "earth": ("earth_pct", 0, 100, "%"), "temperature": ("temp_max_k", 100, 400, "K"),
    "safety": ("s_safety", 0, 1, "score"), "ice": ("s_ice", 0, 1, "score"),
}


def _ramp(n=256):
    import matplotlib

    cm = matplotlib.colormaps["viridis"]
    return (cm(np.linspace(0, 1, n))[:, :3] * 255).astype(np.uint8)


def _flags(tab, cfg):
    f = np.zeros(tab["lat"].size, np.uint16)
    f |= (~tab["landing_safe"]).astype(np.uint16) << stub.FLAGS["off_market"]
    p95 = np.percentile(tab["viability"], cfg["badges"]["hot_property_pct"])
    f |= (tab["viability"] >= p95).astype(np.uint16) << stub.FLAGS["hot_property"]
    limb = (np.abs(tab["lon"]) >= 80) & (np.abs(tab["lon"]) <= 100)
    f |= (limb & (tab["earth_frac"] >= cfg["badges"]["earth_view_frac"])).astype(np.uint16) << stub.FLAGS["earth_view"]
    return f


def _columns(tab, cfg):
    tile = stub._tile_index(tab["lon"], tab["lat"], np.array([[-180], [-90]]), np.array([[180], [90]]))
    order = np.argsort(tile, kind="stable")
    t = tile[order]
    start = np.r_[0, np.flatnonzero(np.diff(t)) + 1]
    row = np.arange(t.size) - np.repeat(start, np.diff(np.r_[start, t.size]))
    u8 = lambda a: np.clip(np.rint(a), 0, 100).astype(np.uint8)
    c = {
        "x": tab["lon"], "y": tab["lat"], "lat": tab["lat"], "lon": tab["lon"], "area_km2": tab["area_km2"],
        "price": tab["price"], "rent_avg": tab["rent_avg"], "viability": u8(tab["viability"]),
        **{f"s_{k}": u8(100 * tab[f"s_{k}"]) for k in ("safety", "power", "comms", "thermal", "landmark", "ice")},
        "sunlit_pct": u8(100 * tab["sunlit_frac"]), "earth_pct": u8(100 * tab["earth_frac"]),
        "slope_mean_ddeg": np.rint(10 * tab["slope_mean_deg"]).astype(np.uint16),
        "longest_dark_h": tab["longest_dark_h"].astype(np.uint16),
        "longest_blackout_h": tab["longest_blackout_h"].astype(np.uint16),
        "temp_min_k": np.rint(tab["temp_min_k"]).astype(np.uint16),
        "temp_max_k": np.rint(tab["temp_max_k"]).astype(np.uint16),
        "ice_km10": np.full(tab["lat"].size, 65535, np.uint16),
        "land_type": tab["land_type"].astype(np.uint8), "flags": _flags(tab, cfg),
        "bw_lander_h": tab["bw_lander_h"].astype(np.uint16), "bw_habitat_h": tab["bw_habitat_h"].astype(np.uint16),
        "bw_lander_start": tab["bw_lander_start"].astype(np.uint16),
        "bw_habitat_start": tab["bw_habitat_start"].astype(np.uint16),
        "tile": tile.astype(np.uint16),
    }
    c = {k: np.asarray(v)[order] for k, v in c.items()}
    c["row_in_tile"] = row.astype(np.uint16)
    return c, order


def _write_detail(d: Path, tab, cols, order, lm):
    (d / "detail").mkdir(exist_ok=True)
    nearby = tab["nearby"][order]
    ids = (tab["lat_idx"][order], tab["lon_idx"][order])
    for t in np.unique(cols["tile"]):
        idx = np.flatnonzero(cols["tile"] == t)
        recs = []
        for i in idx:
            j = order[i]
            recs.append({
                "row": int(cols["row_in_tile"][i]), "id": f"G-{ids[0][i]:03d}-{ids[1][i]:03d}",
                "land_type": land.LAND_TYPES[int(cols["land_type"][i])],
                "slope_p90_deg": round(float(tab["slope_p90_deg"][j]), 1), "roughness_m": round(float(tab["roughness_m"][j]), 1),
                "relief_m": round(float(tab["relief_m"][j])), "safe_area_frac": round(float(tab["safe_area_frac"][j]), 3),
                "landing_safe": bool(tab["landing_safe"][j]), "energy_wh_m2_day": round(float(tab["energy_wh_m2_day"][j])),
                "longest_light_h": int(tab["longest_light_h"][j]), "mean_earth_el_deg": round(float(tab["mean_earth_el"][j]), 1),
                "temp_mean_k": round(float(tab["temp_mean_k"][j])),
                "monthly_sunlit_pct": [int(round(100 * v)) for v in tab["monthly_sunlit"][j]],
                "monthly_earth_pct": [int(round(100 * v)) for v in tab["monthly_earth"][j]],
                "nearby": [lm["name"][k] for k in nearby[i] if k >= 0],
            })
        tx, ty = int(t) % stub.N_TILES_AXIS, int(t) // stub.N_TILES_AXIS
        (d / "detail" / f"{tx}_{ty}.json").write_text(json.dumps(recs, separators=(",", ":")))


def _write_overlays(d: Path, tab, size=(1440, 720)):
    (d / "overlay").mkdir(exist_ok=True)
    ramp = _ramp()
    legend_stops = [[round(x, 2), "#%02x%02x%02x" % tuple(ramp[int(x * 255)])] for x in (0, 0.25, 0.5, 0.75, 1.0)]
    for name, (field, lo, hi, unit) in OVERLAY_FIELDS.items():
        v = tab[field] if field in tab else {"sunlit_pct": 100 * tab["sunlit_frac"], "earth_pct": 100 * tab["earth_frac"]}[field]
        grid = np.flipud(np.asarray(v, float).reshape(180, 360))  # north-up raster
        img = np.clip((grid - lo) / (hi - lo), 0, 1)
        idx = np.asarray(Image.fromarray((img * 255).astype(np.uint8)).resize(size, Image.BILINEAR))
        rgba = np.dstack([ramp[idx], np.full(idx.shape, 200, np.uint8)])
        Image.fromarray(rgba, "RGBA").save(d / "overlay" / f"{name}.png", optimize=True)
        (d / "overlay" / f"{name}.json").write_text(json.dumps(
            {"name": name, "label": name.title(), "unit": unit, "min": lo, "max": hi, "ramp": legend_stops,
             "size": list(size), "extent": [-180, -90, 180, 90]}))


def _write_basemap(d: Path, dem_npy, size=(8192, 4096)):
    dem = np.load(dem_npy).astype(np.float32)
    gy, gx = np.gradient(dem, 950.0)  # ~950 m cells; vertical exaggeration x3
    gx, gy = 3 * gx, 3 * gy
    az, alt = np.radians(315), np.radians(45)
    shade = (np.sin(alt) + np.cos(alt) * (gx * np.sin(az) + gy * np.cos(az))) / np.sqrt(1 + gx**2 + gy**2)
    g = (np.clip(shade, 0, 1) * 215 + 25).astype(np.uint8)
    Image.fromarray(g, "L").resize(size, Image.LANCZOS).convert("RGB").save(d / "basemap.jpg", quality=82)


def write_manifest(out: Path, tiers: dict, cfg, counts: dict | None = None):
    old = {}
    if (out / "manifest.json").exists():
        old = json.loads((out / "manifest.json").read_text())
    counts = {**old.get("counts", {}), **(counts or {})}
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json")
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True,
                                      cwd=Path(__file__).parent, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        sha = "unknown"
    m = {
        "contract_version": CONTRACT_VERSION, "stub": any(v == "stub" for v in tiers.values()), "tiers": tiers,
        "pipeline_sha": sha, "generated_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "analysis_year": cfg["analysis"]["year"], "steps": stub.N_STEPS, "counts": counts,
        "config_sha256": hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16],
        "horizon": old.get("horizon", {}), "tiles_per_axis": stub.N_TILES_AXIS,
        "files": [{"path": p.relative_to(out).as_posix(), "bytes": p.stat().st_size,
                   "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
    }
    (out / "manifest.json").write_text(json.dumps(m, indent=1))
    return m


def export_global(tab: dict, cfg: dict, out, dem_npy) -> dict:
    out = Path(out)
    d = out / "global"
    d.mkdir(parents=True, exist_ok=True)
    cols, order = _columns(tab, cfg)
    n = stub._write_cols(d, cols, "global")
    meta = json.loads((d / "cols.json").read_text())
    meta["land_types"] = land.LAND_TYPES
    (d / "cols.json").write_text(json.dumps(meta, indent=1))
    lm = land.load_landmarks()
    _write_detail(d, tab, cols, order, lm)
    _write_overlays(d, tab)
    _write_basemap(d, dem_npy)
    (out / "landmarks.json").write_text(json.dumps(
        [{"name": str(n_), "type": str(t), "lat": float(la), "lon": float(lo), "fame": {"apollo_artemis": 100, "major_crater": 60, "other": 30}[str(f)]}
         for n_, t, la, lo, f in zip(lm["name"], lm["type"], lm["lat"], lm["lon"], lm["fame_class"], strict=True)],
        separators=(",", ":")))
    from . import config

    config.export(cfg, out / "config.json", {"scarcity_viability_cutoff": float(tab["scarcity_cutoff"])})
    return write_manifest(out, {"global": "real", "polar": "stub"}, cfg, {"global": n})
