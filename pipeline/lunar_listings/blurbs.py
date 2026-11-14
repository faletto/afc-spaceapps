"""Deterministic listing blurbs and 'why' lines (spec §3.10, DET-6/DET-2). Templates: config/blurbs.yaml."""
import hashlib
import operator
from pathlib import Path

import yaml

PATH = Path(__file__).resolve().parents[2] / "config" / "blurbs.yaml"
_OPS = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt, "==": operator.eq, "!=": operator.ne}
_T = None


def templates():
    global _T
    if _T is None:
        _T = yaml.safe_load(PATH.read_text())
    return _T


def _cond(c: str, facts: dict) -> bool:
    name, op, val = c.split(" ", 2)
    f = facts[name]
    return _OPS[op](f, float(val)) if isinstance(f, (int, float)) and val.strip() != "" else _OPS[op](str(f), val.strip())


def _matches(t, facts):
    return all(_cond(c, facts) for c in t["if"])


def pick(plot_id: str, n: int, salt: str = "") -> int:
    return int.from_bytes(hashlib.sha256((plot_id + salt).encode()).digest()[:4], "big") % n


def _fmt(text, facts):
    ex = {"sun_pct": round(100 * facts["sunlit"]), "earth_pct": round(100 * facts["earth"]),
          "tmax_k": round(facts["tmax_k"]), "ice_km_round": round(facts["ice_km"], 1),
          "psr_temp_c": round(40 - 273.15), "dark_days": round(facts["dark_h"] / 24), "nearby": facts["nearby"]}
    return text.format(**{**facts, **ex})


def blurb(plot_id: str, facts: dict) -> str:
    t = templates()
    ms = [x for x in t["lead"] if _matches(x, facts)]
    top = max(x["pri"] for x in ms)
    lead = [x for x in ms if x["pri"] == top]
    s1 = _fmt(lead[pick(plot_id, len(lead))]["text"], facts)
    ex = [x for x in t["extra"] if _matches(x, facts)]
    if ex and facts["safe"]:
        s1 += " " + _fmt(ex[pick(plot_id, len(ex), "x")]["text"], facts)
    return s1


def why(sub: dict) -> str:
    """One line from the strongest sub-scores (0..1 each): high (>= 0.5) prices up, low (<= 0.2) prices down."""
    w = templates()["why"]
    ups, downs = [], []
    for k, v in sub.items():
        if w.get(f"{k}_high") and v >= 0.5:
            ups.append((v, w[f"{k}_high"]))
        if w.get(f"{k}_low") and v <= 0.2:
            downs.append((1 - v, w[f"{k}_low"]))
    ups = [t for _, t in sorted(ups, reverse=True)[:2]]
    downs = [t for _, t in sorted(downs, reverse=True)[:1]]
    if not ups and not downs:
        return "Priced as a typical lunar lot"
    if ups and downs:
        return f"Priced up for {' and '.join(ups)}, down for {downs[0]}"
    return f"Priced up for {' and '.join(ups)}" if ups else f"Priced down for {downs[0]}"
