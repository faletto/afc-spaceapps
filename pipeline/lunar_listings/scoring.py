"""Sub-scores and viability (spec §3.9). All inputs are numpy arrays (or scalars); outputs are 0..1 floats."""
import numpy as np

from .terrain import norm


def penalty(h, h50, k):
    """Smooth logistic in hours: 1 at h=0, 0.5 at h=h50, -> 0 as h grows."""
    return 1.0 / (1.0 + (np.asarray(h, float) / h50) ** k)


def thermal_hazard(temp_min_k, temp_max_k, cfg):
    """Mean of cold hazard (colder = worse) and swing hazard, both 0..1."""
    th = cfg["thermal"]
    cold = 1.0 - norm(temp_min_k, th["cold_range_k"])
    swing = norm(np.asarray(temp_max_k) - np.asarray(temp_min_k), th["swing_range_k"])
    return (cold + swing) / 2


def subscores(t: dict, cfg: dict, polar: bool = False) -> dict:
    """t: table with energy_wh_m2_day, longest_dark_h, earth_frac, longest_blackout_h, hazard_score,
    temp_min_k, temp_max_k, landmark_score, (ice_km for polar)."""
    pen = cfg["penalty"]
    s = {
        "safety": 1.0 - np.asarray(t["hazard_score"]),
        "power": norm(t["energy_wh_m2_day"], cfg["norm"]["energy_wh_m2_day"])
        * penalty(t["longest_dark_h"], pen["dark"]["h50"], pen["dark"]["k"]),
        "comms": np.asarray(t["earth_frac"])
        * penalty(t["longest_blackout_h"], pen["blackout"]["h50"], pen["blackout"]["k"]),
        "thermal": 1.0 - thermal_hazard(t["temp_min_k"], t["temp_max_k"], cfg),
        "landmark": np.asarray(t["landmark_score"], float),
    }
    if polar:
        s["ice"] = 1.0 - norm(t["ice_km"], (0, cfg["ice"]["max_km"]))
    else:
        s["ice"] = np.zeros_like(s["safety"])
    return s


def viability(s: dict, landing_safe, cfg: dict, cap: float = 10.0, weights: dict | None = None) -> np.ndarray:
    """0..100. Unsafe plots are capped (Off market)."""
    w = weights or cfg["weights"]
    num = sum(w.get(k, 0.0) * s[k] for k in s)
    v = 100.0 * num / sum(w.get(k, 0.0) for k in s)
    return np.where(landing_safe, v, np.minimum(v, cap))


def named_scores(s: dict) -> dict:
    names = {"safety": "Landing", "power": "Sun", "comms": "Signal", "thermal": "Comfort",
             "landmark": "Views", "ice": "Ice"}
    return {names[k]: np.rint(100 * np.asarray(v)).astype(np.uint8) for k, v in s.items()}
