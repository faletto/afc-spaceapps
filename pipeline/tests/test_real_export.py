"""Checks the committed real export (skipped when the tier is still stub)."""

import json
from pathlib import Path

import numpy as np
import pytest

D = Path(__file__).resolve().parents[2] / "app" / "public" / "data"
m = json.loads((D / "manifest.json").read_text()) if (D / "manifest.json").exists() else {}
pytestmark = pytest.mark.skipif(m.get("tiers", {}).get("global") != "real", reason="global tier is stub")


def test_global_cols_real():
    meta = json.loads((D / "global" / "cols.json").read_text())
    buf = (D / "global" / "cols.bin").read_bytes()
    g = {
        c["name"]: np.frombuffer(buf, np.dtype(c["dtype"]).newbyteorder("<"), meta["rows"], c["offset"])
        for c in meta["columns"]
    }
    assert meta["rows"] == 64800 and meta["land_types"][0] == "highlands"
    assert g["price"].min() >= 5000 and g["viability"].max() <= 100
    assert abs(g["area_km2"].sum() - 4 * np.pi * 1737.4**2) < 100
    # rows sorted by tile; detail files line up
    assert (np.diff(g["tile"].astype(int)) >= 0).all()
    t = int(g["tile"][0])
    rec = json.loads((D / "global" / "detail" / f"{t % 16}_{t // 16}.json").read_text())
    assert len(rec) == (g["tile"] == t).sum() and rec[0]["id"].startswith("G-")
    # near side sees Earth, far side doesn't
    near = (abs(g["lon"]) < 20) & (abs(g["lat"]) < 20)
    far = (abs(abs(g["lon"]) - 180) < 20) & (abs(g["lat"]) < 20)
    assert g["earth_pct"][near].mean() > 99 and g["earth_pct"][far].mean() < 1


def test_ephemeris_bin_is_real_not_stub():
    from lunar_listings import ephemeris

    e = ephemeris.load()
    a = np.fromfile(D / "ephemeris.bin", dtype="<f4")
    n = len(e["tsi"])
    assert a.size == n * 8
    assert np.allclose(a[: n * 3].reshape(-1, 3), e["sun_xyz"], atol=1e-6)
    assert np.allclose(a[n * 3 : n * 6].reshape(-1, 3), e["earth_xyz"], atol=1e-6)
    assert np.allclose(a[n * 7 :], e["tsi"], rtol=1e-6) and 1300 < a[n * 7 :].min()
