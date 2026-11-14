"""M0 stub generator: fake data in the real §5 formats (contract v1). Values are plausible, not physical."""
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

from . import CONTRACT_VERSION, config

N_STEPS = 8784  # 2028 is a leap year: 366 * 24
N_TILES_AXIS = 16
HORIZON_AZ = 180  # 2-degree az steps; uint8 = elevation in HORIZON_UNIT_DEG
HORIZON_UNIT_DEG = 0.25
HORIZON_OFFSET_DEG = -10.0  # elevation = v * unit + offset (allows negative horizons)
R = 1_737_400.0

# (name, dtype, scale) in file order. real value = stored * scale.
COLUMNS = [
    ("x", "float32", 1), ("y", "float32", 1), ("lat", "float32", 1), ("lon", "float32", 1),
    ("area_km2", "float32", 1), ("price", "float32", 1), ("rent_avg", "float32", 1),
    ("viability", "uint8", 1),
    ("s_safety", "uint8", 1), ("s_power", "uint8", 1), ("s_comms", "uint8", 1),
    ("s_thermal", "uint8", 1), ("s_landmark", "uint8", 1), ("s_ice", "uint8", 1),
    ("sunlit_pct", "uint8", 1), ("earth_pct", "uint8", 1),
    ("slope_mean_ddeg", "uint16", 0.1),
    ("longest_dark_h", "uint16", 1), ("longest_blackout_h", "uint16", 1),
    ("temp_min_k", "uint16", 1), ("temp_max_k", "uint16", 1),
    ("ice_km10", "uint16", 0.1),  # 65535 = n/a
    ("land_type", "uint8", 1), ("flags", "uint16", 1),
    ("bw_lander_h", "uint16", 1), ("bw_habitat_h", "uint16", 1),
    ("bw_lander_start", "uint16", 1), ("bw_habitat_start", "uint16", 1),
    ("tile", "uint16", 1), ("row_in_tile", "uint16", 1),
]
LAND_TYPES = ["mare", "highland", "crater_floor", "rim", "ridge", "psr_edge"]
FLAGS = {"off_market": 0, "hot_property": 1, "price_cut": 2, "earth_view": 3, "featured": 4, "tier_polar": 15}
OVERLAYS = ["viability", "sunlit", "earth", "temperature", "safety", "ice"]
LANDMARKS = [
    ("Apollo 11", "apollo", 0.67, 23.47, 100), ("Apollo 12", "apollo", -3.01, -23.42, 80),
    ("Apollo 14", "apollo", -3.65, -17.47, 75), ("Apollo 15", "apollo", 26.13, 3.63, 85),
    ("Apollo 16", "apollo", -8.97, 15.50, 80), ("Apollo 17", "apollo", 20.19, 30.77, 90),
    ("Tycho", "crater", -43.31, -11.36, 85), ("Copernicus", "crater", 9.62, -20.08, 80),
    ("Shackleton", "crater", -89.9, 0.0, 95), ("Malapert Massif", "massif", -85.9, 12.9, 70),
    ("Connecting Ridge", "ridge", -89.4, -129.0, 60), ("Mons Huygens", "mountain", 19.9, -3.2, 55),
]


def _rng():
    return np.random.default_rng(20281114)


def _tile_index(x, y, lo, hi):
    f = (np.asarray([x, y]) - lo) / (hi - lo)
    t = np.clip((f * N_TILES_AXIS).astype(int), 0, N_TILES_AXIS - 1)
    return t[1] * N_TILES_AXIS + t[0]


def _plots(tier: str):
    """Return dict of x, y, lat, lon, area, tile (rows sorted by tile)."""
    if tier == "global":
        lat = np.repeat(np.arange(-89.5, 90, 1.0), 360)
        lon = np.tile(np.arange(-179.5, 180, 1.0), 180)
        x, y = lon.copy(), lat.copy()
        area = R**2 * np.radians(1.0) * (np.sin(np.radians(lat + 0.5)) - np.sin(np.radians(lat - 0.5))) / 1e6
        tile = _tile_index(x, y, np.array([[-180], [-90]]), np.array([[180], [90]]))
    else:
        rmax = R * np.radians(5.0)  # 85 degS, azimuthal-equidistant stand-in
        step = 960.0
        ax = np.arange(-rmax + step / 2, rmax, step)
        gx, gy = np.meshgrid(ax, ax)
        gx, gy = gx.ravel(), gy.ravel()
        keep = np.hypot(gx, gy) <= rmax
        x, y = gx[keep], gy[keep]
        r = np.hypot(x, y)
        lat = -90 + np.degrees(r / R)
        lon = np.degrees(np.arctan2(x, y))
        area = np.full(x.size, 0.960**2)
        tile = _tile_index(x, y, np.array([[-rmax], [-rmax]]), np.array([[rmax], [rmax]]))
    order = np.argsort(tile, kind="stable")
    d = {k: np.asarray(v)[order] for k, v in {"x": x, "y": y, "lat": lat, "lon": lon, "area": area, "tile": tile}.items()}
    t = d["tile"]
    start = np.r_[0, np.flatnonzero(np.diff(t)) + 1]
    first = np.repeat(start, np.diff(np.r_[start, t.size]))
    d["row_in_tile"] = np.arange(t.size) - first
    return d


def _columns(tier: str, p: dict, rng) -> dict:
    n = p["x"].size
    lat, lon = p["lat"], p["lon"]
    smooth = 0.5 + 0.5 * np.sin(np.radians(lat * 3 + lon * 2))
    noise = rng.random(n)
    u8 = lambda a: np.clip(a, 0, 100).astype(np.uint8)
    viability = u8(20 + 60 * smooth + 15 * noise)
    cfg = config.load()["price"]
    price = cfg["base_usd"] * (1 + cfg["k"] * viability / 100)  # fake: real model is pricing.py
    flags = np.zeros(n, np.uint16)
    flags |= ((noise > 0.97).astype(np.uint16) << FLAGS["off_market"])
    flags |= ((viability > 80).astype(np.uint16) << FLAGS["hot_property"])
    flags |= ((noise < 0.03).astype(np.uint16) << FLAGS["price_cut"])
    if tier == "polar":
        flags |= np.uint16(1 << FLAGS["tier_polar"])
    polar = np.clip((np.abs(lat) - 60) / 30, 0, 1)
    c = {
        "x": p["x"], "y": p["y"], "lat": lat, "lon": lon, "area_km2": p["area"], "price": price, "rent_avg": price * cfg["rent_ratio"],
        "viability": viability,
        "s_safety": u8(30 + 60 * noise), "s_power": u8(20 + 70 * smooth), "s_comms": u8(90 - 40 * polar - 10 * noise),
        "s_thermal": u8(40 + 40 * polar + 10 * noise), "s_landmark": u8(100 * rng.random(n) ** 3),
        "s_ice": u8(100 * polar * noise),
        "sunlit_pct": u8(40 + 55 * smooth - 10 * noise), "earth_pct": u8(90 - 50 * polar * noise),
        "slope_mean_ddeg": (10 + 100 * noise).astype(np.uint16),
        "longest_dark_h": (100 + 350 * (1 - smooth) + 50 * noise).astype(np.uint16),
        "longest_blackout_h": (50 + 300 * polar * noise).astype(np.uint16),
        "temp_min_k": (40 + 90 * (1 - polar)).astype(np.uint16), "temp_max_k": (250 + 120 * (1 - polar)).astype(np.uint16),
        "ice_km10": np.where(polar > 0.8, (noise * 300).astype(np.uint16), 65535).astype(np.uint16),
        "land_type": (noise * len(LAND_TYPES)).astype(np.uint8) % len(LAND_TYPES), "flags": flags,
        "bw_lander_h": (300 + 400 * smooth).astype(np.uint16), "bw_habitat_h": (600 + 900 * smooth).astype(np.uint16),
        "bw_lander_start": (1 + 365 * noise).astype(np.uint16), "bw_habitat_start": (1 + 365 * smooth).astype(np.uint16),
        "tile": p["tile"].astype(np.uint16), "row_in_tile": p["row_in_tile"].astype(np.uint16),
    }
    return c


def _tier_geo(tier: str) -> dict:
    if tier == "global":
        return {"projection": {"type": "lonlat"}, "bounds": [-180, -90, 180, 90]}
    rmax = R * np.radians(5.0)
    return {"projection": {"type": "azimuthal_equidistant_south", "lat0": -90, "R": R, "stub": True},
            "bounds": [-rmax, -rmax, rmax, rmax]}


def _write_cols(d: Path, cols: dict, tier: str) -> int:
    d.mkdir(parents=True, exist_ok=True)
    meta, buf, off = [], bytearray(), 0
    n = cols["x"].size
    for name, dtype, scale in COLUMNS:
        raw = np.ascontiguousarray(cols[name]).astype(np.dtype(dtype).newbyteorder("<")).tobytes()
        meta.append({"name": name, "dtype": dtype, "offset": off, "scale": scale})
        buf += raw
        pad = (-len(buf)) % 4
        buf += b"\0" * pad
        off = len(buf)
    (d / "cols.bin").write_bytes(bytes(buf))
    (d / "cols.json").write_text(json.dumps(
        {"rows": n, "columns": meta, "land_types": LAND_TYPES, "flags": FLAGS,
         "tiles_per_axis": N_TILES_AXIS, **_tier_geo(tier)}, indent=1))
    return n


def _write_tiles(d: Path, tier: str, cols: dict, rng):
    (d / "detail").mkdir(exist_ok=True)
    tile = cols["tile"]
    for t in np.unique(tile):
        idx = np.flatnonzero(tile == t)
        recs = [{"row": int(cols["row_in_tile"][i]), "name": f"{tier.title()} plot {i}",
                 "blurb": "Stub listing.", "sunlit_monthly": [int(v) for v in (cols["sunlit_pct"][i] + rng.integers(-5, 6, 12)).clip(0, 100)]}
                for i in idx]
        tx, ty = int(t) % N_TILES_AXIS, int(t) // N_TILES_AXIS
        (d / "detail" / f"{tx}_{ty}.json").write_text(json.dumps(recs, separators=(",", ":")))
        if tier == "polar":
            (d / "horizon").mkdir(exist_ok=True)
            az = np.arange(HORIZON_AZ)
            elev = (cols["slope_mean_ddeg"][idx] / 10.0)[:, None] * (1 + 0.5 * np.sin(np.radians(az * 6 + idx[:, None] % 360)))
            h = (elev - HORIZON_OFFSET_DEG) / HORIZON_UNIT_DEG
            (d / "horizon" / f"{tx}_{ty}.bin").write_bytes(h.clip(0, 255).astype(np.uint8).tobytes())


def _write_overlays(d: Path, tier: str, size):
    (d / "overlay").mkdir(exist_ok=True)
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    for k, name in enumerate(OVERLAYS):
        v = 0.5 + 0.5 * np.sin(xx / w * 6.28 * (1 + k % 3) + yy / h * 3.14 * (1 + k))
        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[..., 0] = 255 * v
        rgba[..., 1] = 255 * (1 - v) * 0.6
        rgba[..., 2] = 255 * (1 - v)
        rgba[..., 3] = 200
        Image.fromarray(rgba, "RGBA").save(d / "overlay" / f"{name}.png", optimize=True)
        (d / "overlay" / f"{name}.json").write_text(json.dumps(
            {"name": name, "label": name.title(), "unit": "%" if name != "temperature" else "K",
             "min": 0, "max": 100, "ramp": [[0, "#0000ff"], [1, "#ff0000"]], "size": [w, h]}))


def _write_basemap(d: Path, size):
    w, h = size
    yy, xx = np.mgrid[0:h:4, 0:w:4]
    g = (110 + 40 * np.sin(xx / 80.0) * np.cos(yy / 60.0)).astype(np.uint8)
    img = Image.fromarray(g, "L").resize((w, h), Image.BILINEAR)
    img.save(d / "basemap.jpg", quality=70)


def _ephemeris(out: Path):
    t = np.arange(N_STEPS, dtype=np.float64)  # hours since 2028-01-01T00:00Z
    sun_ang = -2 * np.pi * t / (27.321661 * 24)
    dec = np.radians(1.54)
    sun = np.stack([np.cos(sun_ang) * np.cos(dec), np.sin(sun_ang) * np.cos(dec), np.full_like(t, np.sin(dec))], 1)
    lib = np.radians(6.7) * np.sin(2 * np.pi * t / (27.554 * 24))
    earth = np.stack([np.cos(lib), np.sin(np.radians(7) * np.sin(2 * np.pi * t / (27.212 * 24))), np.sin(lib)], 1)
    earth /= np.linalg.norm(earth, axis=1, keepdims=True)
    dist = 384_400e3 * (1 - 0.0549 * np.cos(2 * np.pi * t / (27.554 * 24)))
    tsi = 1361 * (1 + 0.0334 * np.cos(2 * np.pi * (t / 24 - 3) / 365.25))
    arr = np.concatenate([sun.ravel(), earth.ravel(), dist, tsi]).astype("<f4")
    assert arr.size == N_STEPS * 8
    out.write_bytes(arr.tobytes())


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True,
                                       cwd=Path(__file__).parent, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def write_stub(out: Path) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    cfg = config.load()
    rng = _rng()
    config.export(cfg, out / "config.json", {"scarcity_viability_cutoff": 85})
    _ephemeris(out / "ephemeris.bin")
    counts = {}
    for tier, osize, bsize in (("global", (1024, 512), (8192, 4096)), ("polar", (1024, 1024), (4096, 4096))):
        d = out / tier
        d.mkdir(exist_ok=True)
        cols = _columns(tier, _plots(tier), rng)
        counts[tier] = _write_cols(d, cols, tier)
        _write_tiles(d, tier, cols, rng)
        _write_overlays(d, tier, osize)
        _write_basemap(d, bsize)
    (out / "landmarks.json").write_text(json.dumps(
        [{"name": n, "type": t, "lat": la, "lon": lo, "fame": f} for n, t, la, lo, f in LANDMARKS]))
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json")
    manifest = {
        "contract_version": CONTRACT_VERSION, "stub": True, "pipeline_sha": _git_sha(),
        "generated_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "analysis_year": cfg["analysis"]["year"], "steps": N_STEPS, "counts": counts,
        "horizon": {"az_count": HORIZON_AZ, "az_step_deg": 2, "unit_deg": HORIZON_UNIT_DEG, "offset_deg": HORIZON_OFFSET_DEG, "dtype": "uint8"},
        "tiles_per_axis": N_TILES_AXIS,
        "files": [{"path": p.relative_to(out).as_posix(), "bytes": p.stat().st_size,
                   "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return manifest
