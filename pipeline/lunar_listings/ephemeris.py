"""Parse Horizons text -> CSV -> unit vectors, distances, TSI (spec §3.2)."""
import re
from pathlib import Path

import numpy as np

L_SUN = 3.828e26
DEFAULT_CSV = Path(__file__).resolve().parents[1] / "data" / "ephemeris_2028.csv"
HEADER = "time_utc,earth_sub_lon,earth_sub_lat,sun_sub_lon,sun_sub_lat,r_sun_km,delta_km"


def parse_horizons(text: str, n_steps: int | None = None) -> list[tuple]:
    """Rows of (time, earth_lon_E, earth_lat, sun_lon_E, sun_lat, r_km, delta_km); longitudes east-positive.

    Fails loudly if the longitude-sign line is missing or unrecognised.
    """
    m = re.search(r"Target pole/equ\s*:.*?\{(East|West)-longitude positive\}", text)
    if not m:
        raise ValueError("Horizons output has no longitude-sign line; refusing to guess")
    west = m.group(1) == "West"
    if "$$SOE" not in text or "$$EOE" not in text:
        raise ValueError("Horizons output missing $$SOE/$$EOE markers")
    body = text.split("$$SOE", 1)[1].split("$$EOE", 1)[0].strip().splitlines()
    cols = [c.strip() for c in re.search(r"\n(\s*Date__.*)\n\*+\n\$\$SOE", text).group(1).split(",")]
    idx = {k: cols.index(k) for k in ("ObsSub-LON", "ObsSub-LAT", "SunSub-LON", "SunSub-LAT", "r", "delta")}
    rows = []
    for line in body:
        p = [x.strip() for x in line.split(",")]
        v = {k: float(p[i]) for k, i in idx.items()}
        if west:
            v["ObsSub-LON"], v["SunSub-LON"] = -v["ObsSub-LON"], -v["SunSub-LON"]
        rows.append((p[0], v["ObsSub-LON"] % 360, v["ObsSub-LAT"], v["SunSub-LON"] % 360, v["SunSub-LAT"],
                     v["r"], v["delta"]))
    if n_steps is not None:
        if len(rows) < n_steps:
            raise ValueError(f"expected >= {n_steps} rows, got {len(rows)}")
        rows = rows[:n_steps]
    return rows


def write_csv(rows, path: Path = DEFAULT_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(HEADER + "\n")
        f.writelines(f"{t},{a:.6f},{b:.6f},{c:.6f},{d:.6f},{r:.3f},{dl:.4f}\n" for t, a, b, c, d, r, dl in rows)


def lonlat_to_unit(lon_deg, lat_deg) -> np.ndarray:
    lo, la = np.radians(lon_deg), np.radians(lat_deg)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], axis=-1)


def load(path: Path = DEFAULT_CSV) -> dict:
    """float64 arrays: sun_xyz, earth_xyz (unit), earth_dist_m, tsi, in the Moon-fixed (ME) frame."""
    a = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=range(1, 7))
    return {
        "sun_xyz": lonlat_to_unit(a[:, 2], a[:, 3]),
        "earth_xyz": lonlat_to_unit(a[:, 0], a[:, 1]),
        "earth_dist_m": a[:, 5] * 1e3,
        "tsi": L_SUN / (4 * np.pi * (a[:, 4] * 1e3) ** 2),
        "r_sun_km": a[:, 4],
    }
