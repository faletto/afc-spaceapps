"""Integrity checks on the committed real export (app/public/data): no stub leftovers, ranges, cross-file consistency."""

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from lunar_listings import config, contract, ephemeris, land, polar, pricing

D = Path(__file__).resolve().parents[2] / "app" / "public" / "data"
pytestmark = pytest.mark.skipif(not (D / "manifest.json").exists(), reason="no exported data")
CFG = config.load()
M = json.loads((D / "manifest.json").read_text()) if (D / "manifest.json").exists() else {}


def cols(tier):
    meta = json.loads((D / tier / "cols.json").read_text())
    buf = (D / tier / "cols.bin").read_bytes()
    g = {
        c["name"]: np.frombuffer(buf, np.dtype(c["dtype"]).newbyteorder("<"), meta["rows"], c["offset"])
        for c in meta["columns"]
    }
    return meta, g


@pytest.fixture(scope="module", params=["global", "polar"])
def tier(request):
    return (request.param, *cols(request.param))


def test_manifest_says_real_and_every_hash_matches():
    assert (
        M["contract_version"] == 2
        and M["stub"] is False
        and M["tiers"] == {"global": "real", "polar": "real"}
    )
    assert M["horizon"]["offset_deg"] == -6.0 and M["horizon"]["unit_deg"] == 0.16 and M["steps"] == 8784
    listed = {f["path"] for f in M["files"]}
    on_disk = {p.relative_to(D).as_posix() for p in D.rglob("*") if p.is_file() and p.name != "manifest.json"}
    assert listed == on_disk  # no orphan or stale files (e.g. leftover stub tiles)
    for f in M["files"]:
        assert hashlib.sha256((D / f["path"]).read_bytes()).hexdigest() == f["sha256"], f["path"]
        assert (D / f["path"]).stat().st_size == f["bytes"]


def test_no_stub_text_anywhere_in_json_assets():
    for p in list(D.rglob("*.json")):
        if p.name == "manifest.json":
            continue
        t = p.read_text()
        assert "Stub listing" not in t and "azimuthal_equidistant_south" not in t, p
        assert '"stub": true' not in t.lower()
    assert "polar_stereographic_south" in (D / "polar" / "cols.json").read_text()


def test_ephemeris_bin_matches_parsed_horizons_csv():
    e = ephemeris.load()
    a = np.fromfile(D / "ephemeris.bin", "<f4")
    n = len(e["tsi"])
    assert a.size == 8 * n == 8 * 8784
    assert np.allclose(a[: 3 * n].reshape(-1, 3), e["sun_xyz"], atol=1e-6)
    assert np.allclose(a[3 * n : 6 * n].reshape(-1, 3), e["earth_xyz"], atol=1e-6)
    assert np.allclose(a[6 * n : 7 * n], e["earth_dist_m"], rtol=1e-6) and np.allclose(
        a[7 * n :], e["tsi"], rtol=1e-6
    )


def test_columns_finite_in_range_and_sorted(tier):
    name, meta, g = tier
    n = meta["rows"]
    assert n == M["counts"][name] and [c["name"] for c in meta["columns"]] == [c[0] for c in contract.COLUMNS]
    for k, v in g.items():
        assert v.shape == (n,) and (np.isfinite(v).all() if v.dtype.kind == "f" else True), k
    assert (g["viability"] <= 100).all() and (g["sunlit_pct"] <= 100).all() and (g["earth_pct"] <= 100).all()
    assert all((g[f"s_{k}"] <= 100).all() for k in ("safety", "power", "comms", "thermal", "landmark", "ice"))
    assert (g["price"] >= CFG["price"]["base_usd"]).all() and (g["area_km2"] > 0).all()
    assert (
        (g["temp_min_k"] >= 40).all()
        and (g["temp_max_k"] <= 450).all()
        and (g["temp_min_k"] <= g["temp_max_k"]).all()
    )
    assert (g["longest_dark_h"] <= 8784).all() and (g["longest_blackout_h"] <= 8784).all()
    assert (g["bw_lander_start"] >= 1).all() and (g["bw_lander_start"] <= 366).all()
    assert (g["bw_lander_h"] <= 14 * 24).all() and (g["bw_habitat_h"] <= 90 * 24).all()
    assert (g["land_type"] < len(meta["land_types"])).all() and (np.diff(g["tile"].astype(int)) >= 0).all()
    assert (
        len(set(zip(g["tile"].tolist(), g["row_in_tile"].tolist(), strict=True))) == n
    )  # unique (tile, row)


def test_flags_and_prices_internally_consistent(tier):
    name, _meta, g = tier
    fl = g["flags"]
    off = (fl & 1).astype(bool)
    assert (g["viability"][off] <= 10).all() and (g["viability"][~off] >= 0).all()
    assert off.any() and not off.all()
    assert np.allclose(g["rent_avg"], CFG["price"]["rent_ratio"] * g["price"], rtol=2e-6)
    floor = CFG["price"]["base_usd"] * np.exp(CFG["price"]["k"] * g["viability"].astype(float) / 100)
    cut = json.loads((D / "config.json").read_text())["computed"]["scarcity_viability_cutoff"]
    # price = floor * (1 + premium) * scarcity (>= floor; viability is rounded to an integer in the file)
    assert (g["price"] >= 0.95 * floor).all() and (g["price"] <= floor * 1.3 * 1.8).all() and cut > 0
    assert ((fl >> contract.FLAGS["tier_polar"]) & 1).astype(bool).all() == (name == "polar")
    hot = ((fl >> contract.FLAGS["hot_property"]) & 1).astype(bool)
    assert 0 < hot.mean() < 0.2 and g["viability"][hot].min() > g["viability"][~hot].mean()
    assert 0 < ((fl >> contract.FLAGS["featured"]) & 1).sum() <= 25


def test_cross_tier_scarcity_cutoff_matches_recomputed():
    _, g = cols("global")
    _, p = cols("polar")
    allv = np.concatenate([g["viability"], p["viability"]]).astype(float)
    cfgj = json.loads((D / "config.json").read_text())
    # the file stores integer viability; the cutoff was computed on the float values, so allow rounding
    assert cfgj["computed"]["scarcity_viability_cutoff"] == pytest.approx(
        pricing.scarcity_cutoff(allv, CFG), abs=0.7
    )
    assert cfgj["power"]["load_w"] == CFG["power"]["load_w"] and cfgj["price"]["k"] == 6.9


def test_tiles_detail_and_horizon_align_with_columns(tier):
    name, meta, g = tier
    seen = 0
    ids = set()
    for t in np.unique(g["tile"]):
        rows = int((g["tile"] == t).sum())
        tx, ty = int(t) % 16, int(t) // 16
        rec = json.loads((D / name / "detail" / f"{tx}_{ty}.json").read_text())
        assert len(rec) == rows and [r["row"] for r in rec] == list(range(rows))
        for r in rec:
            ids.add(r["id"])
            assert (
                r["blurb"] and r["why"].startswith("Priced") and r["nearest_feature"] and r["nearest_km"] >= 0
            )
            assert len(r["monthly_sunlit_pct"]) == 12 and all(
                0 <= x <= 100 for x in r["monthly_sunlit_pct"] + r["monthly_earth_pct"]
            )
        i0 = int(np.flatnonzero(g["tile"] == t)[0])
        assert rec[0]["land_type"] == meta["land_types"][g["land_type"][i0]]
        if name == "polar":
            assert (D / "polar" / "horizon" / f"{tx}_{ty}.bin").stat().st_size == 180 * rows
        seen += rows
    assert seen == meta["rows"] and len(ids) == meta["rows"]  # plot ids are unique


def test_polar_geometry_matches_projection_and_horizons_are_plausible():
    meta, g = cols("polar")
    la, lo = polar.xy_to_lonlat(g["x"].astype(float), g["y"].astype(float))
    assert np.allclose(la, g["lat"], atol=2e-3) and (g["lat"] <= -84.9).all()
    assert (
        np.abs(((lo - g["lon"] + 180) % 360) - 180).max() < 0.05 or np.abs(g["lat"]).min() > 89
    )  # lon agrees away from the pole
    assert np.hypot(g["x"], g["y"]).max() < 152_000 and meta["bounds"] == [-153600, -153600, 153600, 153600]
    tot = []
    for t in np.unique(g["tile"])[::7]:
        b = np.fromfile(D / "polar" / "horizon" / f"{int(t) % 16}_{int(t) // 16}.bin", np.uint8).reshape(
            -1, 180
        )
        tot.append(b)
        assert (b < 255).mean() > 0.999  # almost nothing saturates at +34.8 deg
    ang = np.concatenate(tot) * 0.16 - 6.0
    assert -6 <= ang.min() and ang.max() <= 34.8 and 0 < np.median(ang) < 10


def test_global_geometry_covers_every_degree_once():
    _meta, g = cols("global")
    cell = set(
        zip(np.floor(g["lat"]).astype(int).tolist(), np.floor(g["lon"]).astype(int).tolist(), strict=True)
    )
    assert len(cell) == 64800 and abs(g["area_km2"].astype(float).sum() - 4 * np.pi * 1737.4**2) < 100
    assert g["lat"].min() == -89.5 and g["lon"].max() == 179.5


def test_landmarks_and_nearby_names_exist():
    lm = json.loads((D / "landmarks.json").read_text())
    names = {x["name"] for x in lm}
    assert (
        len(lm) > 1400
        and {"Apollo 11", "Apollo 17"} <= names
        and all(-90 <= x["lat"] <= 90 and -180 <= x["lon"] <= 180 for x in lm)
    )
    assert any(x["name"].startswith("Artemis III region") for x in lm)
    _meta, g = cols("global")
    t = int(g["tile"][5000])
    for r in json.loads((D / "global" / "detail" / f"{t % 16}_{t // 16}.json").read_text())[:40]:
        assert set(r["nearby"]) <= names


def test_images_decode_with_expected_sizes_and_overlays_have_legends():
    sizes = {
        "global/basemap.jpg": (8192, 4096),
        "global/basemap_small.jpg": (2048, 1024),
        "polar/basemap.jpg": (4096, 4096),
        "polar/basemap_small.jpg": (1024, 1024),
    }
    for p, s in sizes.items():
        with Image.open(D / p) as im:
            assert im.size == s, p
    for t, s in (("global", (1440, 720)), ("polar", (1024, 1024))):
        for name in ("viability", "sunlit", "earth", "temperature", "safety", "ice"):
            lg = json.loads((D / t / "overlay" / f"{name}.json").read_text())
            with Image.open(D / t / "overlay" / f"{name}.png") as im:
                assert im.size == s == tuple(lg["size"]) and im.mode == "RGBA"
                a = np.asarray(im)
                assert a[..., 3].max() > 0 and a[..., :3].std() > 5  # not blank
            assert lg["min"] < lg["max"] and len(lg["ramp"]) >= 2
    pa = np.asarray(Image.open(D / "polar" / "overlay" / "viability.png"))[..., 3]
    assert pa[0, 0] == 0 and pa[512, 512] > 0  # outside the disc transparent, centre opaque


def test_glossary_follows_config_and_has_required_ids():
    g = json.loads((D / "glossary.json").read_text())
    need = [
        "sunlight",
        "longest_night",
        "earth_contact",
        "longest_blackout",
        "temperature",
        "slope",
        "land_type",
        "ice",
        "viability",
        "landing",
        "sun_score",
        "signal",
        "comfort",
        "views",
        "ice_score",
    ]
    assert set(need) <= set(g) and all(g[k]["text"] for k in need)
    assert (
        all("{" not in str(v) for e in g.values() for v in e.values())
        and f"{CFG['power']['load_w']:g} W" in g["sun_score"]["text"]
    )
    assert "modelled" in g["temperature"]["text"].lower()
    assert land.LAND_TYPES == json.loads((D / "global" / "cols.json").read_text())["land_types"]


def test_committed_horizons_csv_is_complete_hourly_2028():
    import csv
    from datetime import datetime, timedelta

    with open(ephemeris.DEFAULT_CSV) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 8784
    t0 = datetime.strptime(rows[0]["time_utc"], "%Y-%b-%d %H:%M")
    assert t0 == datetime(2028, 1, 1) and datetime.strptime(
        rows[-1]["time_utc"], "%Y-%b-%d %H:%M"
    ) == datetime(2028, 12, 31, 23)
    ts = [datetime.strptime(r["time_utc"], "%Y-%b-%d %H:%M") for r in rows]
    assert all(b - a == timedelta(hours=1) for a, b in itertools.pairwise(ts))  # no gaps, no duplicates
    e = ephemeris.load()
    assert (
        356e6 < e["earth_dist_m"].min()
        and e["earth_dist_m"].max() < 407e6
        and 1300 < e["tsi"].min()
        and e["tsi"].max() < 1420
    )
    assert np.all(
        np.abs(np.diff(np.unwrap(np.radians(np.degrees(np.arctan2(e["sun_xyz"][:, 1], e["sun_xyz"][:, 0]))))))
        < 0.02
    )  # smooth sub-solar longitude


def test_dem_sources_are_all_pinned():
    import yaml

    from lunar_listings.fetch import dem

    spec = yaml.safe_load(dem.SOURCES.read_text())
    assert len(spec["files"]) >= 10 and all(
        len(f["sha256"] or "") == 64 and f["bytes"] > 0 for f in spec["files"]
    )
    assert all(
        f["url"].startswith("https://")
        and ("nasa.gov" in f["url"] or "usgs.gov" in f["url"] or "wustl.edu" in f["url"])
        for f in spec["files"]
    )
