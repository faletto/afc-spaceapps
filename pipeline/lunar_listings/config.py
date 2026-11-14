"""Load + validate config/lunar-listings.yaml; export config.json for the app."""
import json
from pathlib import Path

import yaml

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config" / "lunar-listings.yaml"
WEIGHT_KEYS = {"safety", "power", "comms", "thermal", "landmark", "ice"}


class ConfigError(ValueError):
    pass


def _need(cond: bool, msg: str):
    if not cond:
        raise ConfigError(msg)


def _range(v, name):
    _need(isinstance(v, list) and len(v) == 2 and v[0] < v[1], f"{name} must be [lo, hi] with lo < hi")


def validate(c: dict) -> dict:
    for k in ("analysis", "moon", "grid", "horizon", "power", "comms", "thermal", "safety", "norm",
              "penalty", "weights", "home_types", "price", "badges", "results", "stays"):
        _need(k in c, f"missing section: {k}")
    _need(c["analysis"]["year"] == int(c["analysis"]["year"]), "analysis.year must be int")
    _need(c["analysis"]["step_hours"] > 0, "analysis.step_hours > 0")
    _need(c["moon"]["radius_m"] > 1e6, "moon.radius_m implausible")
    _need(-90 < c["grid"]["polar"]["lat_min"] < 0, "grid.polar.lat_min in (-90, 0)")
    _need(c["grid"]["polar"]["plot_m"] % c["grid"]["polar"]["cell_m"] == 0, "plot_m must be a multiple of cell_m")
    pw = c["power"]
    _need(all(pw[k] > 0 for k in ("area_m2", "efficiency", "load_w", "net_ref_w", "battery_wh_per_kg", "battery_ref_kg")),
          "power.area_m2/efficiency/load_w/net_ref_w/battery_* must be > 0")
    _need(c["comms"]["mode"] in ("terrain_margin", "absolute"), "comms.mode: terrain_margin|absolute")
    _need(c["comms"]["margin_deg"] >= 0 and c["comms"]["cutoff_deg"] >= 0, "comms angles >= 0")
    for r in ("cold_range_k", "swing_range_k"):
        _range(c["thermal"][r], f"thermal.{r}")
    for r in ("slope_p90_range", "roughness_range_m", "relief_range_m"):
        _range(c["safety"][r], f"safety.{r}")
    _range(c["norm"]["energy_wh_m2_day"], "norm.energy_wh_m2_day")
    _need(0 < c["safety"]["min_safe_frac"] <= 1, "safety.min_safe_frac in (0, 1]")
    _need(set(c["weights"]) == WEIGHT_KEYS, f"weights keys must be {sorted(WEIGHT_KEYS)}")
    _need(all(w >= 0 for w in c["weights"].values()) and sum(c["weights"].values()) > 0, "weights >= 0, sum > 0")
    for name, h in c["home_types"].items():
        if name == "min_results":
            continue
        _need(set(h["weights"]) <= WEIGHT_KEYS, f"home_types.{name}.weights unknown key")
        _need(h["ref_stay_days"] in c["stays"], f"home_types.{name}.ref_stay_days must be in stays")
    p = c["price"]
    _need(p["base_usd"] > 0 and p["k"] > 0, "price.base_usd, k > 0")
    _need(0 < p["range"]["polar"] <= p["range"]["global"] < 1, "price.range: 0 < polar <= global < 1")
    _need(p["rent_ratio"] > 0, "price.rent_ratio > 0")
    _need(all(isinstance(s, int) and s > 0 for s in c["stays"]), "stays must be positive ints")
    _need(c["results"]["max_cards"] > 0, "results.max_cards > 0")
    return c


def load(path: Path = DEFAULT_PATH) -> dict:
    with open(path) as f:
        return validate(yaml.safe_load(f))


def export(c: dict, out: Path, extra: dict | None = None) -> None:
    """Write config.json. `extra` carries computed values (e.g. scarcity_viability_cutoff)."""
    d = dict(c)
    d["computed"] = {"scarcity_viability_cutoff": None, **(extra or {})}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(d, indent=1, sort_keys=True))
