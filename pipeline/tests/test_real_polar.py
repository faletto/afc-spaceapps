"""Real polar export + science sanity (skipped while the tier is stub)."""
import json
from pathlib import Path

import numpy as np
import pytest

from lunar_listings import polar

D = Path(__file__).resolve().parents[2] / "app" / "public" / "data"
m = json.loads((D / "manifest.json").read_text()) if (D / "manifest.json").exists() else {}
pytestmark = pytest.mark.skipif(m.get("tiers", {}).get("polar") != "real", reason="polar tier is stub")


@pytest.fixture(scope="module")
def pol():
    meta = json.loads((D / "polar" / "cols.json").read_text())
    buf = (D / "polar" / "cols.bin").read_bytes()
    g = {c["name"]: np.frombuffer(buf, np.dtype(c["dtype"]).newbyteorder("<"), meta["rows"], c["offset"]) for c in meta["columns"]}
    return meta, g


def test_structure_and_files(pol):
    meta, g = pol
    assert meta["projection"]["type"] == "polar_stereographic_south" and meta["bounds"][2] == 153600
    assert (np.diff(g["tile"].astype(int)) >= 0).all()
    for t in np.unique(g["tile"])[:20]:
        rows = int((g["tile"] == t).sum())
        tx, ty = int(t) % 16, int(t) // 16
        assert (D / "polar" / "horizon" / f"{tx}_{ty}.bin").stat().st_size == rows * 180
        assert len(json.loads((D / "polar" / "detail" / f"{tx}_{ty}.json").read_text())) == rows
    lat, lon = polar.xy_to_lonlat(g["x"].astype(float), g["y"].astype(float))
    assert np.allclose(lat, g["lat"], atol=1e-3) and g["lat"].max() <= -84.9
    assert m["horizon"]["offset_deg"] == -6.0 and m["horizon"]["unit_deg"] == 0.16


def _near(g, lat, lon, r=3000):
    x, y = polar.lonlat_to_xy(lat, lon)
    return np.hypot(g["x"] - x, g["y"] - y) < r


def test_shackleton_floor_dark_and_ridge_top_tier(pol):
    _, g = pol
    floor = _near(g, -89.9, 129.8, 1500)
    assert np.median(g["sunlit_pct"][floor]) < 1 and np.median(g["temp_max_k"][floor]) < 60  # rim plots at the edge may be lit
    ridge = _near(g, -89.45, -129.0)
    assert g["viability"][ridge].max() >= np.percentile(g["viability"], 99)
    assert g["sunlit_pct"].max() >= 70  # some plot is mostly sunlit


def test_psr_share_and_offmarket(pol):
    _, g = pol
    psr = (g["sunlit_pct"] < 1).mean()
    assert 0.05 < psr < 0.3
    off = (g["flags"] & 1).astype(bool)
    assert 0.1 < off.mean() < 0.7 and (g["viability"][off] <= 10).all()


def test_horizon_tile_decodes_to_plausible_angles(pol):
    _, g = pol
    t = int(g["tile"][len(g["tile"]) // 2])
    b = np.fromfile(D / "polar" / "horizon" / f"{t % 16}_{t // 16}.bin", np.uint8).reshape(-1, 180)
    ang = b * 0.16 - 6.0
    assert -6 <= ang.min() and ang.max() < 36 and ang.mean() > 0


def test_blurbs_why_and_featured_flags(pol):
    _, g = pol
    t = int(g["tile"][0])
    rec = json.loads((D / "polar" / "detail" / f"{t % 16}_{t // 16}.json").read_text())
    assert all(r["blurb"] and r["why"].startswith("Priced") and "{" not in r["blurb"] for r in rec)
    feat = (g["flags"] >> 4) & 1
    assert 5 <= feat.sum() <= 20
