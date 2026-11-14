"""Shared data-contract constants and writers (spec §5, CONTRACT.md): used by the real export and the stub."""
import json
from pathlib import Path

import numpy as np

N_STEPS = 8784  # 2028 is a leap year: 366 * 24
N_TILES_AXIS = 16
HORIZON_AZ = 180  # 2-degree azimuth steps
HZ_UNIT_DEG, HZ_OFFSET_DEG = 0.16, -6.0  # horizon uint8: elevation = v * unit + offset (spec said -3; real skylines reach -5.8)
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
FLAGS = {"off_market": 0, "hot_property": 1, "price_cut": 2, "earth_view": 3, "featured": 4, "tier_polar": 15}


def tile_index(x, y, lo, hi):
    f = (np.asarray([x, y]) - lo) / (hi - lo)
    t = np.clip((f * N_TILES_AXIS).astype(int), 0, N_TILES_AXIS - 1)
    return t[1] * N_TILES_AXIS + t[0]


def cast_column(arr, dtype: str) -> np.ndarray:
    """Cast to the contract dtype without silent wrap-around: integers saturate, NaN/inf become 0 / the dtype limits."""
    dt = np.dtype(dtype)
    a = np.asarray(arr)
    if dt.kind in "iu":
        info = np.iinfo(dt)
        a = np.clip(np.nan_to_num(a.astype(float), nan=0.0, posinf=info.max, neginf=info.min), info.min, info.max)
        return np.rint(a).astype(dt)
    return a.astype(dt)


def write_cols(d: Path, cols: dict, tier: str, land_types: list, geo: dict) -> int:
    d.mkdir(parents=True, exist_ok=True)
    meta, buf, off = [], bytearray(), 0
    n = cols["x"].size
    for name, dtype, scale in COLUMNS:
        raw = np.ascontiguousarray(cast_column(cols[name], dtype)).astype(np.dtype(dtype).newbyteorder("<")).tobytes()
        meta.append({"name": name, "dtype": dtype, "offset": off, "scale": scale})
        buf += raw
        pad = (-len(buf)) % 4
        buf += b"\0" * pad
        off = len(buf)
    (d / "cols.bin").write_bytes(bytes(buf))
    (d / "cols.json").write_text(json.dumps(
        {"rows": n, "columns": meta, "land_types": land_types, "flags": FLAGS,
         "tiles_per_axis": N_TILES_AXIS, **geo}, indent=1))
    return n


