"""Real-data export in the contract formats (spec §3.11, §5). Global tier now; polar added in P4.

Only writes `<out>/global/**` and refreshes manifest.json; other tiers stay as they are.
"""

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

from . import CONTRACT_VERSION, blurbs, contract, land

OVERLAY_FIELDS = {  # name -> (table field, lo, hi, unit)
    "viability": ("viability", 0, 100, "score"),
    "sunlit": ("sunlit_pct", 0, 100, "%"),
    "earth": ("earth_pct", 0, 100, "%"),
    "temperature": ("temp_max_k", 100, 400, "K"),
    "safety": ("s_safety", 0, 1, "score"),
    "ice": ("s_ice", 0, 1, "score"),
}


def _ramp(n=256):
    import matplotlib

    cm = matplotlib.colormaps["viridis"]
    return (cm(np.linspace(0, 1, n))[:, :3] * 255).astype(np.uint8)


def _flags(tab, cfg, hot_cut, polar=False):
    f = np.zeros(tab["lat"].size, np.uint16)
    f |= (~tab["landing_safe"]).astype(np.uint16) << contract.FLAGS["off_market"]
    f |= (tab["viability"] >= hot_cut).astype(np.uint16) << contract.FLAGS["hot_property"]
    limb = (
        np.ones(tab["lat"].size, bool) if polar else (np.abs(tab["lon"]) >= 80) & (np.abs(tab["lon"]) <= 100)
    )
    f |= (limb & (tab["earth_frac"] >= cfg["badges"]["earth_view_frac"])).astype(np.uint16) << contract.FLAGS[
        "earth_view"
    ]
    if "featured" in tab:
        f |= tab["featured"].astype(np.uint16) << contract.FLAGS["featured"]
    if polar:
        f |= np.uint16(1 << contract.FLAGS["tier_polar"])
    return f


def _columns(tab, cfg, hot_cut, polar=False):
    if polar:
        h = polar_build_half()
        tile = contract.tile_index(tab["x"], tab["y"], np.array([[-h], [-h]]), np.array([[h], [h]]))
    else:
        tile = contract.tile_index(tab["lon"], tab["lat"], np.array([[-180], [-90]]), np.array([[180], [90]]))
    order = np.argsort(tile, kind="stable")
    t = tile[order]
    start = np.r_[0, np.flatnonzero(np.diff(t)) + 1]
    row = np.arange(t.size) - np.repeat(start, np.diff(np.r_[start, t.size]))
    u8 = lambda a: np.clip(np.rint(a), 0, 100).astype(np.uint8)
    c = {
        "x": tab["x"] if polar else tab["lon"],
        "y": tab["y"] if polar else tab["lat"],
        "lat": tab["lat"],
        "lon": tab["lon"],
        "area_km2": tab["area_km2"],
        "price": tab["price"],
        "rent_avg": tab["rent_avg"],
        "viability": u8(tab["viability"]),
        **{
            f"s_{k}": u8(100 * tab[f"s_{k}"])
            for k in ("safety", "power", "comms", "thermal", "landmark", "ice")
        },
        "sunlit_pct": u8(100 * tab["sunlit_frac"]),
        "earth_pct": u8(100 * tab["earth_frac"]),
        "slope_mean_ddeg": np.rint(10 * tab["slope_mean_deg"]).astype(np.uint16),
        "longest_dark_h": tab["longest_dark_h"].astype(np.uint16),
        "longest_blackout_h": tab["longest_blackout_h"].astype(np.uint16),
        "temp_min_k": np.rint(tab["temp_min_k"]).astype(np.uint16),
        "temp_max_k": np.rint(tab["temp_max_k"]).astype(np.uint16),
        "ice_km10": np.minimum(np.rint(10 * tab["ice_km"]), 65534)
        if polar
        else np.full(tab["lat"].size, 65535, np.uint16),
        "land_type": tab["land_type"].astype(np.uint8),
        "flags": _flags(tab, cfg, hot_cut, polar),
        "bw_lander_h": tab["bw_lander_h"].astype(np.uint16),
        "bw_habitat_h": tab["bw_habitat_h"].astype(np.uint16),
        "bw_lander_start": tab["bw_lander_start"].astype(np.uint16),
        "bw_habitat_start": tab["bw_habitat_start"].astype(np.uint16),
        "tile": tile.astype(np.uint16),
    }
    c = {k: np.asarray(v)[order] for k, v in c.items()}
    c["row_in_tile"] = row.astype(np.uint16)
    return c, order


def _write_detail(d: Path, tab, cols, order, lm):
    (d / "detail").mkdir(exist_ok=True)
    nn_i, nn_km = land.nearest_landmark(tab["lat"], tab["lon"], lm)
    nearby = tab["nearby"][order]
    ids = (tab["lat_idx"][order], tab["lon_idx"][order])
    for t in np.unique(cols["tile"]):
        idx = np.flatnonzero(cols["tile"] == t)
        recs = []
        for i in idx:
            j = order[i]
            recs.append(
                {
                    "row": int(cols["row_in_tile"][i]),
                    "id": f"G-{ids[0][i]:03d}-{ids[1][i]:03d}",
                    "land_type": land.LAND_TYPES[int(cols["land_type"][i])],
                    "slope_p90_deg": round(float(tab["slope_p90_deg"][j]), 1),
                    "roughness_m": round(float(tab["roughness_m"][j]), 1),
                    "relief_m": round(float(tab["relief_m"][j])),
                    "safe_area_frac": round(float(tab["safe_area_frac"][j]), 3),
                    "landing_safe": bool(tab["landing_safe"][j]),
                    "energy_wh_m2_day": round(float(tab["energy_wh_m2_day"][j])),
                    "longest_light_h": int(tab["longest_light_h"][j]),
                    "mean_earth_el_deg": round(float(tab["mean_earth_el"][j]), 1),
                    "temp_mean_k": round(float(tab["temp_mean_k"][j])),
                    "monthly_sunlit_pct": [round(100 * v) for v in tab["monthly_sunlit"][j]],
                    "monthly_earth_pct": [round(100 * v) for v in tab["monthly_earth"][j]],
                    "nearby": [lm["name"][k] for k in nearby[i] if k >= 0],
                }
            )
            recs[-1].update(nearest_feature=str(lm["name"][nn_i[j]]), nearest_km=round(float(nn_km[j]), 1))
            recs[-1].update(
                _text_fields(tab, j, recs[-1]["id"], recs[-1]["land_type"], False, recs[-1]["nearby"])
            )
        tx, ty = int(t) % contract.N_TILES_AXIS, int(t) // contract.N_TILES_AXIS
        (d / "detail" / f"{tx}_{ty}.json").write_text(json.dumps(recs, separators=(",", ":")))


def _write_overlays(d: Path, tab, size=(1440, 720)):
    (d / "overlay").mkdir(exist_ok=True)
    ramp = _ramp()
    legend_stops = [
        [round(x, 2), "#{:02x}{:02x}{:02x}".format(*tuple(ramp[int(x * 255)]))]
        for x in (0, 0.25, 0.5, 0.75, 1.0)
    ]
    for name, (field, lo, hi, unit) in OVERLAY_FIELDS.items():
        v = (
            tab[field]
            if field in tab
            else {"sunlit_pct": 100 * tab["sunlit_frac"], "earth_pct": 100 * tab["earth_frac"]}[field]
        )
        grid = np.flipud(np.asarray(v, float).reshape(180, 360))  # north-up raster
        img = np.clip((grid - lo) / (hi - lo), 0, 1)
        idx = np.asarray(Image.fromarray((img * 255).astype(np.uint8)).resize(size, Image.BILINEAR))
        rgba = np.dstack([ramp[idx], np.full(idx.shape, 200, np.uint8)])
        Image.fromarray(rgba, "RGBA").save(d / "overlay" / f"{name}.png", optimize=True)
        (d / "overlay" / f"{name}.json").write_text(
            json.dumps(
                {
                    "name": name,
                    "label": name.title(),
                    "unit": unit,
                    "min": lo,
                    "max": hi,
                    "ramp": legend_stops,
                    "size": list(size),
                    "extent": [-180, -90, 180, 90],
                }
            )
        )


def _write_basemap(d: Path, dem_npy, size=(8192, 4096)):
    dem = np.load(dem_npy).astype(np.float32)
    gy, gx = np.gradient(dem, 950.0)  # ~950 m cells; vertical exaggeration x3
    gx, gy = 3 * gx, 3 * gy
    az, alt = np.radians(315), np.radians(45)
    shade = (np.sin(alt) + np.cos(alt) * (gx * np.sin(az) + gy * np.cos(az))) / np.sqrt(1 + gx**2 + gy**2)
    g = (np.clip(shade, 0, 1) * 215 + 25).astype(np.uint8)
    img = Image.fromarray(g, "L").resize(size, Image.LANCZOS).convert("RGB")
    img.save(d / "basemap.jpg", quality=78)
    img.resize((size[0] // 4, size[1] // 4), Image.LANCZOS).save(d / "basemap_small.jpg", quality=80)


def _sources() -> dict:
    """Provenance of the polar terrain (DEM + slope product actually used), from data/work."""
    f = Path(__file__).resolve().parents[2] / "data" / "work" / "terrain_polar_source.json"
    base = {
        "ephemeris": "JPL Horizons (DE441), 2028 hourly",
        "global_dem": "LRO LOLA 118 m (USGS)",
        "landmarks": "IAU/USGS nomenclature",
    }
    return {**base, **({"polar": json.loads(f.read_text())} if f.exists() else {})}


def write_manifest(out: Path, tiers: dict, cfg, counts: dict | None = None):
    old = {}
    if (out / "manifest.json").exists():
        old = json.loads((out / "manifest.json").read_text())
    counts = {**old.get("counts", {}), **(counts or {})}
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json")
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True,
            cwd=Path(__file__).parent,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        sha = "unknown"
    m = {
        "contract_version": CONTRACT_VERSION,
        "stub": any(v != "real" for v in tiers.values()),
        "tiers": tiers,
        "pipeline_sha": sha,
        "generated_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "analysis_year": cfg["analysis"]["year"],
        "steps": contract.N_STEPS,
        "counts": counts,
        "config_sha256": hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16],
        "sources": _sources(),
        "horizon": old.get("horizon", {}),
        "tiles_per_axis": contract.N_TILES_AXIS,
        "files": [
            {
                "path": p.relative_to(out).as_posix(),
                "bytes": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            }
            for p in files
        ],
    }
    (out / "manifest.json").write_text(json.dumps(m, indent=1))
    return m


def write_ephemeris(out: Path) -> None:
    """ephemeris.bin (contract §5): float32 LE sun_xyz[N*3], earth_xyz[N*3], earth_dist_m[N], tsi[N] from the real CSV."""
    from . import ephemeris

    e = ephemeris.load()
    arr = np.concatenate([e["sun_xyz"].ravel(), e["earth_xyz"].ravel(), e["earth_dist_m"], e["tsi"]]).astype(
        "<f4"
    )
    assert arr.size == len(e["tsi"]) * 8
    (Path(out) / "ephemeris.bin").write_bytes(arr.tobytes())


def export_global(tab: dict, cfg: dict, out, dem_npy, hot_cut=None, cutoff=None) -> dict:
    hot_cut = (
        float(np.percentile(tab["viability"], cfg["badges"]["hot_property_pct"]))
        if hot_cut is None
        else hot_cut
    )
    out = Path(out)
    d = out / "global"
    d.mkdir(parents=True, exist_ok=True)
    write_ephemeris(out)
    tab = {**tab, "featured": featured_mask(tab, land.load_landmarks(), False)}
    cols, order = _columns(tab, cfg, hot_cut)
    n = contract.write_cols(
        d, cols, "global", land.LAND_TYPES, {"projection": {"type": "lonlat"}, "bounds": [-180, -90, 180, 90]}
    )
    lm = land.load_landmarks()
    _write_detail(d, tab, cols, order, lm)
    _write_overlays(d, tab)
    _write_basemap(d, dem_npy)
    (out / "landmarks.json").write_text(
        json.dumps(
            [
                {
                    "name": str(n_),
                    "type": str(t),
                    "lat": float(la),
                    "lon": float(lo),
                    "fame": {"apollo_artemis": 100, "major_crater": 60, "other": 30}[str(f)],
                }
                for n_, t, la, lo, f in zip(
                    lm["name"], lm["type"], lm["lat"], lm["lon"], lm["fame_class"], strict=True
                )
            ],
            separators=(",", ":"),
        )
    )
    from . import config

    gl = (Path(__file__).resolve().parents[2] / "config" / "glossary.json").read_text()
    for k, v in cfg[
        "power"
    ].items():  # glossary text follows the config, so changing the model needs no text edits
        if isinstance(v, (int, float)):
            gl = gl.replace("{" + k + ":g}", f"{v:g}")
    (out / "glossary.json").write_text(gl)
    config.export(
        cfg,
        out / "config.json",
        {"scarcity_viability_cutoff": float(tab["scarcity_cutoff"] if cutoff is None else cutoff)},
    )
    return write_manifest(
        out,
        {
            "global": "real",
            "polar": json.loads((out / "manifest.json").read_text())["tiers"].get("polar", "missing")
            if (out / "manifest.json").exists()
            else "missing",
        },
        cfg,
        {"global": n},
    )


def polar_build_half():
    from .terrain import POLAR_HALF_M

    return POLAR_HALF_M


PROJECTION_POLAR = {
    "type": "polar_stereographic_south",
    "lat0": -90,
    "lon0": 0,
    "R": 1737400.0,
    "k0": 1.0,
    "forward": "x = rho*sin(lon), y = rho*cos(lon), rho = 2R*tan(45deg + lat/2); lon east-positive",
    "azimuth": "bearing a (0=local N, 90=E) -> map direction (sin(lon+a), cos(lon+a))",
}


def _write_polar_detail(d: Path, tab, cols, order, lm):
    (d / "detail").mkdir(exist_ok=True)
    nn_i, nn_km = land.nearest_landmark(tab["lat"], tab["lon"], lm)
    nearby = tab["nearby"][order]
    for t in np.unique(cols["tile"]):
        idx = np.flatnonzero(cols["tile"] == t)
        recs = []
        for i in idx:
            j = order[i]
            recs.append(
                {
                    "row": int(cols["row_in_tile"][i]),
                    "id": f"SP-{int(tab['plot_row'][j]):04d}-{int(tab['plot_col'][j]):04d}",
                    "land_type": land.LAND_TYPES[int(cols["land_type"][i])],
                    "best_cell_xy": [round(float(tab["best_x"][j])), round(float(tab["best_y"][j]))],
                    "slope_p90_deg": round(float(tab["slope_p90_deg"][j]), 1),
                    "roughness_m": round(float(tab["roughness_m"][j]), 1),
                    "relief_m": round(float(tab["relief_m"][j])),
                    "safe_area_frac": round(float(tab["safe_area_frac"][j]), 3),
                    "landing_safe": bool(tab["landing_safe"][j]),
                    "energy_wh_m2_day": round(float(tab["energy_wh_m2_day"][j])),
                    "longest_light_h": int(tab["longest_light_h"][j]),
                    "mean_earth_el_deg": round(float(tab["mean_earth_el"][j]), 1),
                    "temp_mean_k": round(float(tab["temp_mean_k"][j])),
                    "ice_km": round(float(tab["ice_km"][j]), 2),
                    "monthly_sunlit_pct": [round(100 * v) for v in tab["monthly_sunlit"][j]],
                    "monthly_earth_pct": [round(100 * v) for v in tab["monthly_earth"][j]],
                    "nearby": [lm["name"][k] for k in nearby[i] if k >= 0],
                }
            )
            recs[-1].update(nearest_feature=str(lm["name"][nn_i[j]]), nearest_km=round(float(nn_km[j]), 1))
            recs[-1].update(
                _text_fields(tab, j, recs[-1]["id"], recs[-1]["land_type"], True, recs[-1]["nearby"])
            )
        tx, ty = int(t) % contract.N_TILES_AXIS, int(t) // contract.N_TILES_AXIS
        (d / "detail" / f"{tx}_{ty}.json").write_text(json.dumps(recs, separators=(",", ":")))


def _write_horizon_tiles(d: Path, tab, cols, order):
    (d / "horizon").mkdir(exist_ok=True)
    for t in np.unique(cols["tile"]):
        idx = np.flatnonzero(cols["tile"] == t)  # already row_in_tile order
        tx, ty = int(t) % contract.N_TILES_AXIS, int(t) // contract.N_TILES_AXIS
        (d / "horizon" / f"{tx}_{ty}.bin").write_bytes(np.ascontiguousarray(tab["hzq"][order][idx]).tobytes())


def _write_polar_overlays(d: Path, tab, size=1024):
    (d / "overlay").mkdir(exist_ok=True)
    ramp = _ramp()
    stops = [
        [round(x, 2), "#{:02x}{:02x}{:02x}".format(*tuple(ramp[int(x * 255)]))]
        for x in (0, 0.25, 0.5, 0.75, 1.0)
    ]
    n = 320
    mask = np.zeros((n, n), np.uint8)
    mask[tab["plot_row"], tab["plot_col"]] = 255
    alpha = np.asarray(Image.fromarray(mask).resize((size, size), Image.NEAREST)) > 0
    fields = {
        "viability": ("viability", 0, 100, "score"),
        "sunlit": ("sunlit_pct", 0, 100, "%"),
        "earth": ("earth_pct", 0, 100, "%"),
        "temperature": ("temp_max_k", 40, 400, "K"),
        "safety": ("s_safety", 0, 1, "score"),
        "ice": ("s_ice", 0, 1, "score"),
    }
    src = dict(tab, sunlit_pct=100 * tab["sunlit_frac"], earth_pct=100 * tab["earth_frac"])
    for name, (f, lo, hi, unit) in fields.items():
        g = np.full((n, n), np.nan, np.float32)
        g[tab["plot_row"], tab["plot_col"]] = src[f]
        g = np.where(np.isnan(g), np.nanmean(g), g)
        v = np.asarray(Image.fromarray(g.astype(np.float32), "F").resize((size, size), Image.BILINEAR))
        idx = (np.clip((v - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
        rgba = np.dstack([ramp[idx], np.where(alpha, 200, 0).astype(np.uint8)])
        Image.fromarray(rgba, "RGBA").save(d / "overlay" / f"{name}.png", optimize=True)
        (d / "overlay" / f"{name}.json").write_text(
            json.dumps(
                {
                    "name": name,
                    "label": name.title(),
                    "unit": unit,
                    "min": lo,
                    "max": hi,
                    "ramp": stops,
                    "size": [size, size],
                    "extent": [
                        -polar_build_half(),
                        -polar_build_half(),
                        polar_build_half(),
                        polar_build_half(),
                    ],
                }
            )
        )


def _write_polar_basemap(d: Path, raw_dir, size=4096):
    import rasterio
    from rasterio.windows import from_bounds

    h = polar_build_half()
    with rasterio.open(Path(raw_dir) / "LDEM_80S_80MPP_ADJ_HILL.TIF") as ds:
        a = ds.read(1, window=from_bounds(-h, -h, h, h, ds.transform).round_offsets().round_lengths())
    a = np.nan_to_num(a.astype(np.float32))
    lo, hi = np.percentile(a, [1, 99])
    g = (np.clip((a - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
    img = Image.fromarray(g, "L").resize((size, size), Image.LANCZOS).convert("RGB")
    img.save(d / "basemap.jpg", quality=78)
    img.resize((size // 4, size // 4), Image.LANCZOS).save(d / "basemap_small.jpg", quality=80)


def export_polar(tab: dict, cfg: dict, out, raw_dir, hot_cut: float, cutoff: float) -> dict:
    out = Path(out)
    d = out / "polar"
    # clear stale stub files in this tier
    import shutil

    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    tab = {**tab, "featured": featured_mask(tab, land.load_landmarks(), True)}
    cols, order = _columns(tab, cfg, hot_cut, polar=True)
    h = polar_build_half()
    n = contract.write_cols(
        d, cols, "polar", land.LAND_TYPES, {"projection": PROJECTION_POLAR, "bounds": [-h, -h, h, h]}
    )
    lm = land.load_landmarks()
    _write_polar_detail(d, tab, cols, order, lm)
    _write_horizon_tiles(d, tab, cols, order)
    _write_polar_overlays(d, tab)
    _write_polar_basemap(d, raw_dir)
    m = json.loads((out / "manifest.json").read_text()) if (out / "manifest.json").exists() else {}
    tiers = {**m.get("tiers", {"global": "missing"}), "polar": "real"}
    mm = write_manifest(out, tiers, cfg, {"polar": n})
    mm["horizon"] = {
        "az_count": contract.HORIZON_AZ,
        "az_step_deg": 2,
        "unit_deg": contract.HZ_UNIT_DEG,
        "offset_deg": contract.HZ_OFFSET_DEG,
        "dtype": "uint8",
    }
    (out / "manifest.json").write_text(json.dumps(mm, indent=1))
    return mm


def featured_mask(tab: dict, lm: dict, polar: bool) -> np.ndarray:
    """Featured plots (for 'Plots for you' and the demo): top-viability plots plus the plots holding the best-known
    landmarks (Apollo/Artemis sites)."""
    n = tab["lat"].size
    m = np.zeros(n, bool)
    m[np.argsort(-tab["viability"])[: 5 if polar else 3]] = True
    sel = np.flatnonzero(
        (lm["fame_class"] == "apollo_artemis") & np.isin(lm["type"], ["artemis"] if polar else ["apollo"])
    )
    for k in sel:
        m[np.argmin(land.great_circle_km(tab["lat"], tab["lon"], lm["lat"][k], lm["lon"][k]))] = True
    return m


def _facts(tab, j, land_name, polar, lm_names):
    ice = float(tab["ice_km"][j]) if polar else 999.0
    return {
        "sunlit": float(tab["sunlit_frac"][j]),
        "earth": float(tab["earth_frac"][j]),
        "land": land_name,
        "ice_km": ice,
        "tmin_k": float(tab["temp_min_k"][j]),
        "tmax_k": float(tab["temp_max_k"][j]),
        "slope_deg": float(tab["slope_mean_deg"][j]),
        "viability": float(tab["viability"][j]),
        "safe": int(bool(tab["landing_safe"][j])),
        "dark_h": float(tab["longest_dark_h"][j]),
        "polar": int(polar),
        "apollo_km": float(tab["apollo_km"][j]),
        "nearby": lm_names,
    }


def _text_fields(tab, j, plot_id, land_name, polar, nearby_names):
    f = _facts(tab, j, land_name, polar, nearby_names[0] if nearby_names else "")
    sub = {k: float(tab[f"s_{k}"][j]) for k in ("safety", "power", "comms", "thermal", "landmark", "ice")}
    if not polar:
        sub.pop("ice")
    return {"blurb": blurbs.blurb(plot_id, f), "why": blurbs.why(sub)}
