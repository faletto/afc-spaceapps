"""Land type, landmarks (spec §3.8). Ice distance for the polar tier is added in P4."""

import csv
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter

from . import terrain

R_KM = 1737.4
LAND_TYPES = ["highlands", "mare", "far_side", "crater_rim", "crater_floor", "psr", "peak_of_light"]
LT = {n: i for i, n in enumerate(LAND_TYPES)}
LANDMARKS_CSV = Path(__file__).resolve().parents[1] / "data" / "landmarks.csv"


def load_landmarks(path: Path = LANDMARKS_CSV) -> dict:
    with open(path) as f:
        rows = list(csv.DictReader(f))
    return {
        "name": np.array([r["name"] for r in rows]),
        "type": np.array([r["type"] for r in rows]),
        "lat": np.array([float(r["lat"]) for r in rows]),
        "lon": np.array([float(r["lon"]) for r in rows]),
        "fame_class": np.array([r["fame_class"] for r in rows]),
    }


def great_circle_km(lat1, lon1, lat2, lon2):
    """Haversine, broadcasting; degrees in, km out."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(lon2 - lon1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def landmark_score_and_nearby(lat, lon, lm: dict, cfg: dict, chunk: int = 2000):
    """score = max_i fame_i * exp(-d_i/d0) in 0..1; nearby = up to max_nearby landmark indices within radius_km."""
    c = cfg["landmarks"]
    fw = np.array([c["fame_weights"][k] for k in lm["fame_class"]])
    n, k = len(lat), c["max_nearby"]
    score = np.zeros(n)
    near = np.full((n, k), -1, np.int32)
    for i in range(0, n, chunk):
        d = great_circle_km(
            lat[i : i + chunk, None], lon[i : i + chunk, None], lm["lat"][None], lm["lon"][None]
        )
        score[i : i + chunk] = (fw[None] * np.exp(-d / c["d0_km"])).max(1)
        order = np.argsort(d, axis=1)[:, :k]
        dsel = np.take_along_axis(d, order, 1)
        near[i : i + chunk, : order.shape[1]] = np.where(
            dsel <= c["radius_km"], order, -1
        )  # fewer landmarks than slots -> -1
    return score, near


def tpi_cells(dem: np.ndarray, radius_km: float, cell_deg: float = 1 / 32) -> np.ndarray:
    """Elevation minus neighbourhood mean (square window of ~2*radius). Longitude wraps; latitude edges reflect."""
    w = max(3, 2 * round(radius_km / (R_KM * np.radians(cell_deg))) + 1)
    return dem - uniform_filter(dem, size=w, mode="reflect")


def plot_tpi_extremes(dem: np.ndarray, radius_km: float):
    """(p90, p10) of the TPI within each plot. A plot-mean TPI is ~0 by construction, so extremes classify."""
    b = terrain.plot_blocks(tpi_cells(dem, radius_km))
    return np.percentile(b, 90, axis=-1), np.percentile(b, 10, axis=-1)


def land_type(
    sunlit_frac, lat, lon, elev_mean_m, tpi_hi, tpi_lo, cfg, polar: bool, median_ref=None
) -> np.ndarray:
    """Rules in priority order (LAND-1). `elev_mean_m` also sets the global-median mare/highland split."""
    ld = cfg["land"]
    sunlit_frac, lon = np.asarray(sunlit_frac), np.asarray(lon)
    out = np.full(sunlit_frac.shape, LT["highlands"], np.uint8)
    ref = np.median(elev_mean_m) if median_ref is None else median_ref  # global plot median (spec)
    out[elev_mean_m < ref - 1000.0] = LT["mare"]
    hi, lo = np.asarray(tpi_hi), np.asarray(tpi_lo)
    out[(lo < ld["tpi_floor"]) & (-lo > hi)] = LT["crater_floor"]
    out[(hi > ld["tpi_rim"]) & (hi >= -lo)] = LT["crater_rim"]
    if not polar:  # "far side" is meaningless within 5 deg of the pole (a lon test there is arbitrary)
        out[np.abs(lon) > 90] = LT["far_side"]
    if polar:
        out[sunlit_frac >= ld["peak_light_frac"]] = LT["peak_of_light"]
    out[sunlit_frac < 0.01] = LT["psr"]
    return out


def apollo_distance_km(lat, lon, lm: dict, chunk: int = 4000) -> np.ndarray:
    """Great-circle distance (km) from each site to the nearest Apollo/Artemis landmark."""
    m = lm["fame_class"] == "apollo_artemis"
    out = np.empty(len(lat))
    for i in range(0, len(lat), chunk):
        d = great_circle_km(
            np.asarray(lat)[i : i + chunk, None],
            np.asarray(lon)[i : i + chunk, None],
            lm["lat"][m][None],
            lm["lon"][m][None],
        )
        out[i : i + chunk] = d.min(1)
    return out


def nearest_landmark(lat, lon, lm: dict, chunk: int = 4000):
    """(index, km) of the nearest landmark for each site."""
    n = len(lat)
    idx, km = np.empty(n, np.int32), np.empty(n)
    for i in range(0, n, chunk):
        d = great_circle_km(
            np.asarray(lat)[i : i + chunk, None],
            np.asarray(lon)[i : i + chunk, None],
            lm["lat"][None],
            lm["lon"][None],
        )
        idx[i : i + chunk], km[i : i + chunk] = d.argmin(1), d.min(1)
    return idx, km
