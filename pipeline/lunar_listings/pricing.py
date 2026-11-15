"""Pricing, rent, badges (spec §3.10). Python reference for the TypeScript mirror (golden vectors)."""

import numpy as np


def scarcity_cutoff(viability, cfg) -> float:
    """Viability at the top scarcity_top_pct quantile; goes into config.json computed values."""
    return float(np.percentile(viability, 100 - cfg["price"]["scarcity_top_pct"]))


def price_usd(viability, cfg, landmark_premium=0.0, cutoff=None) -> np.ndarray:
    p = cfg["price"]
    v = np.asarray(viability, float)
    base = p["base_usd"] * np.exp(p["k"] * v / 100.0) * (1.0 + np.asarray(landmark_premium))
    if cutoff is not None:
        base = base * np.where(v >= cutoff, p["scarcity_mult"], 1.0)
    return base


def landmark_premium(apollo_km, land_type_is_peak, cfg) -> np.ndarray:
    """Apollo/Artemis premium within apollo_radius_km, plus peak_light_premium on Peak-of-light plots (additive)."""
    p = cfg["price"]
    return np.where(np.asarray(apollo_km) <= p["apollo_radius_km"], p["apollo_premium"], 0.0) + np.where(
        land_type_is_peak, p["peak_light_premium"], 0.0
    )


def price_range(price, cfg, polar: bool):
    u = cfg["price"]["range"]["polar" if polar else "global"]
    return price * (1 - u), price * (1 + u)


def rent_per_month(price, cfg):
    """RENT_RATIO * price. For a 1-year stay this is the Buy-side average (RENT-5)."""
    return cfg["price"]["rent_ratio"] * np.asarray(price)


def format_usd(x: float) -> str:
    """3 significant figures, trailing zeros trimmed, K/M/B suffix: $4.2M, $340K, $5K, $1.23M."""
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if x >= div * 0.9995:
            return f"${float(f'{x / div:.3g}'):g}{suf}"
    return f"${x:.0f}"


BADGE_PRIORITY = ["off_market", "hot_property", "peak_of_light", "earth_view", "price_cut"]


def badges(flags: dict, max_per_card: int = 2) -> list[str]:
    return [b for b in BADGE_PRIORITY if flags.get(b)][:max_per_card]


def window_eph(eph: dict, move_in_day: int, stay_days: int) -> tuple[dict, int]:
    """Slice the hourly ephemeris to [move_in, move_in + stay), clipped to the analysis year. Day 1 = Jan 1."""
    n = len(eph["tsi"])
    a = 24 * (move_in_day - 1)
    b = min(n, a + 24 * stay_days)
    if not 0 <= a < b:
        raise ValueError("move-in outside the analysis year")
    return {k: v[a:b] for k, v in eph.items()}, a


def rent_for_stay(site: dict, eph: dict, cfg: dict, cutoff: float, move_in_day: int, stay_days: int) -> dict:
    """Rent Moonstimate (RENT-2) for one plot's best cell: recompute SOL/COMM/TEMP over the stay window, then
    viability_stay -> price(viability_stay) -> RENT_RATIO * price. Safety/landmark/ice terms are unchanged.

    site: lat, lon, horizon_deg[180], hazard_score, landmark_score, landing_safe, premium, ice_km (None if Moon-wide).
    Stays that run past the end of the analysis year are clipped to it.
    """
    from . import scoring, visibility

    w, a = window_eph(eph, move_in_day, stay_days)
    st = visibility.site_stats(
        np.array([site["lat"]]),
        np.array([site["lon"]]),
        np.asarray(site["horizon_deg"], float)[None],
        w,
        cfg,
        start_hour=a,
    )
    t = {
        k: st[k]
        for k in (
            "energy_wh_m2_day",
            "longest_dark_h",
            "earth_frac",
            "longest_blackout_h",
            "temp_min_k",
            "temp_max_k",
        )
    }
    t["hazard_score"] = np.array([site["hazard_score"]])
    t["landmark_score"] = np.array([site["landmark_score"]])
    polar = site.get("ice_km") is not None
    if polar:
        t["ice_km"] = np.array([site["ice_km"]])
    sub = scoring.subscores(t, cfg, polar=polar)
    v = float(scoring.viability(sub, np.array([site["landing_safe"]]), cfg)[0])
    price = float(price_usd(v, cfg, site["premium"], cutoff))
    rent = float(rent_per_month(price, cfg))
    hours = len(w["tsi"])
    return {
        "viability_stay": v,
        "price_stay": price,
        "rent_per_month": rent,
        "stay_hours": hours,
        "total_stay": rent * hours / 24.0 / (365.25 / 12.0),
    }
