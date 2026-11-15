"""Export helpers on small synthetic tables: saturating casts, flags, featured plots, manifest, ephemeris writer."""

import json

import numpy as np
import pytest

from lunar_listings import config, contract, export, land

CFG = config.load()


def test_cast_column_saturates_instead_of_wrapping():
    assert contract.cast_column(np.array([-5, 70000, 300.4, np.nan, np.inf, -np.inf]), "uint16").tolist() == [
        0,
        65535,
        300,
        0,
        65535,
        0,
    ]
    assert contract.cast_column(np.array([-1, 256, 255.6]), "uint8").tolist() == [0, 255, 255]
    assert contract.cast_column(np.array([1.5, np.nan]), "float32").dtype == np.float32
    assert contract.cast_column(np.array([40000.0]), "int16").tolist() == [32767]


def _tab(n=40, polar=False):
    rng = np.random.default_rng(2)
    lat = rng.uniform(-89, 89, n) if not polar else rng.uniform(-89.9, -85, n)
    lon = rng.uniform(-179, 179, n)
    t = {
        "lat": lat,
        "lon": lon,
        "x": rng.uniform(-1e5, 1e5, n),
        "y": rng.uniform(-1e5, 1e5, n),
        "area_km2": np.ones(n),
        "viability": rng.uniform(0, 100, n),
        "landing_safe": rng.random(n) > 0.2,
        "earth_frac": rng.random(n),
        "price": rng.uniform(5e3, 1e6, n),
        "rent_avg": rng.uniform(100, 1e4, n),
        "sunlit_frac": rng.random(n),
        "slope_mean_deg": rng.uniform(0, 30, n),
        "longest_dark_h": rng.integers(0, 8784, n),
        "longest_blackout_h": rng.integers(0, 8784, n),
        "temp_min_k": rng.uniform(40, 100, n),
        "temp_max_k": rng.uniform(100, 390, n),
        "land_type": rng.integers(0, 7, n),
        "bw_lander_h": rng.integers(0, 336, n),
        "bw_habitat_h": rng.integers(0, 2160, n),
        "bw_lander_start": rng.integers(1, 366, n),
        "bw_habitat_start": rng.integers(1, 366, n),
        "ice_km": rng.uniform(0, 200, n),
    }
    for k in ("safety", "power", "comms", "thermal", "landmark", "ice"):
        t[f"s_{k}"] = rng.random(n)
    return t


@pytest.mark.parametrize("polar", [False, True])
def test_columns_sorted_by_tile_row_in_tile_and_value_ranges(polar):
    t = _tab(polar=polar)
    cols, order = export._columns(t, CFG, hot_cut=90.0, polar=polar)
    assert sorted(order.tolist()) == list(range(40)) and (np.diff(cols["tile"].astype(int)) >= 0).all()
    for tl in np.unique(cols["tile"]):
        assert cols["row_in_tile"][cols["tile"] == tl].tolist() == list(range((cols["tile"] == tl).sum()))
    assert (
        cols["viability"].max() <= 100 and cols["ice_km10"].max() < 65535
        if polar
        else (cols["ice_km10"] == 65535).all()
    )


def test_flags_bits():
    t = _tab()
    t["viability"] = np.array([95.0] + [10.0] * 39)
    t["landing_safe"] = np.array([True] * 39 + [False])
    t["earth_frac"] = np.ones(40)
    t["lon"] = np.array([90.0] + [0.0] * 39)
    t["featured"] = np.array([False, True] + [False] * 38)
    f = export._flags(t, CFG, hot_cut=90.0)
    assert f[0] & 2 and f[0] & 8 and not f[0] & 1  # hot + earth view (limb), landable
    assert (
        f[39] & 1 and not f[39] & 2 and f[1] & 16 and not f[2] & 8
    )  # off market; featured; near side has no Earth-view badge
    fp = export._flags(t, CFG, hot_cut=90.0, polar=True)
    assert (fp & (1 << 15)).all() and (
        fp & 8
    ).all()  # polar tier bit; polar plots with 100% Earth get the badge


def test_featured_mask_counts_and_landmark_plots():
    lm = land.load_landmarks()
    n = 500
    rng = np.random.default_rng(1)
    lat, lon = rng.uniform(-60, 60, n), rng.uniform(-180, 180, n)
    lat[7], lon[7] = 0.674, 23.473  # a plot at Apollo 11
    v = rng.uniform(0, 50, n)
    v[100] = 99
    m = export.featured_mask({"lat": lat, "lon": lon, "viability": v}, lm, polar=False)
    assert m[7] and m[100] and 3 <= m.sum() <= 3 + 6
    mp = export.featured_mask(
        {
            "lat": np.full(50, -89.0) + rng.random(50) * 0.1,
            "lon": rng.uniform(-180, 180, 50),
            "viability": rng.random(50),
        },
        lm,
        polar=True,
    )
    assert mp.sum() >= 5


def test_manifest_and_ephemeris_writer(tmp_path):
    export.write_ephemeris(tmp_path)
    assert (tmp_path / "ephemeris.bin").stat().st_size == 8784 * 8 * 4
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "f.bin").write_bytes(b"abc")
    m = export.write_manifest(tmp_path, {"global": "real", "polar": "stub"}, CFG, {"global": 3})
    assert (
        m["stub"] is True
        and m["counts"]["global"] == 3
        and {f["path"] for f in m["files"]} == {"ephemeris.bin", "a/f.bin"}
    )
    m2 = export.write_manifest(tmp_path, {"global": "real", "polar": "real"}, CFG, {"polar": 5})
    assert m2["stub"] is False and m2["counts"] == {"global": 3, "polar": 5}
    assert json.loads((tmp_path / "manifest.json").read_text())["contract_version"] == 2


def test_stub_refuses_to_overwrite_real_data(tmp_path, capsys):
    from lunar_listings import cli

    (tmp_path / "manifest.json").write_text(json.dumps({"tiers": {"global": "real", "polar": "stub"}}))
    assert cli.main(["stub", "--out", str(tmp_path)]) == 1
    assert "refusing" in capsys.readouterr().err
