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
        land_type_is_peak, p["peak_light_premium"], 0.0)


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
