"""Edge cases: ephemeris parsing, geometry, projection, config validation, contract helpers."""
import copy

import numpy as np
import pytest
import yaml

from lunar_listings import config, contract, ephemeris, geometry, polar

HEAD = """Target pole/equ : MOON_ME                         {East-longitude positive}
 Date__(UT)__HR:MN, , , ObsSub-LON, ObsSub-LAT,  SunSub-LON, SunSub-LAT,                r,       rdot,             delta,     deldot,
*****
$$SOE
{rows}
$$EOE
"""
ROW = " 2028-Jan-01 {h:02d}:00, , , {a}, {b}, {c}, {d}, 1.47E+08, 0.5, 4.0E+05, 0.0,"


def _txt(n=3, **kw):
    r = "\n".join(ROW.format(h=i, a=kw.get("a", 10.0), b=-2.0, c=kw.get("c", 100.0), d=-0.5) for i in range(n))
    return HEAD.replace("{rows}", r)


# ------------------------------------------------------------------ ephemeris
def test_parse_rows_and_n_steps_slice():
    assert len(ephemeris.parse_horizons(_txt(5))) == 5
    assert len(ephemeris.parse_horizons(_txt(5), n_steps=3)) == 3
    with pytest.raises(ValueError, match="expected"):
        ephemeris.parse_horizons(_txt(2), n_steps=3)


@pytest.mark.parametrize("mutate", [
    lambda t: t.replace("$$SOE", ""), lambda t: t.replace("$$EOE", ""),
    lambda t: t.replace("{East-longitude positive}", ""),
])
def test_parse_fails_loudly_on_malformed(mutate):
    with pytest.raises(ValueError):
        ephemeris.parse_horizons(mutate(_txt()))


def test_west_positive_and_wraparound():
    east = ephemeris.parse_horizons(_txt(1, a=0.0, c=0.0))[0]
    west = ephemeris.parse_horizons(_txt(1, a=0.0, c=0.0).replace("East-", "West-"))[0]
    assert east[1] == west[1] == 0.0  # -0 % 360 == 0
    w = ephemeris.parse_horizons(_txt(1, a=359.5).replace("East-", "West-"))[0]
    assert w[1] == pytest.approx(0.5)


def test_lonlat_to_unit_poles_and_batch():
    u = ephemeris.lonlat_to_unit(np.array([0.0, 123.0, 0.0]), np.array([90.0, -90.0, 0.0]))
    assert np.allclose(u, [[0, 0, 1], [0, 0, -1], [1, 0, 0]], atol=1e-12)
    assert np.allclose(np.linalg.norm(ephemeris.lonlat_to_unit(np.random.rand(50) * 360, np.random.rand(50) * 180 - 90), axis=1), 1)


def test_csv_roundtrip(tmp_path):
    rows = ephemeris.parse_horizons(_txt(4))
    ephemeris.write_csv(rows, tmp_path / "e.csv")
    e = ephemeris.load(tmp_path / "e.csv")
    assert e["sun_xyz"].shape == (4, 3) and np.allclose(e["earth_dist_m"], 4.0e8) and 1300 < e["tsi"].min()


# ------------------------------------------------------------------ geometry
@pytest.mark.parametrize("lat,lon", [(0, 0), (90, 0), (-90, 0), (-90, 137), (45, -179.9), (89.999, 10), (-33.3, 270)])
def test_enu_frame_orthonormal_right_handed(lat, lon):
    u, e, n = geometry.enu_frame(lat, lon)
    M = np.array([e, n, u])
    assert np.allclose(M @ M.T, np.eye(3), atol=1e-12)
    assert np.allclose(np.cross(e, n), u, atol=1e-12)  # east x north = up


def test_azimuth_cardinals_and_wrap():
    u, e, n = geometry.enu_frame(10, 20)
    for vec, az in ((n, 0), (e, 90), (-n, 180), (-e, 270)):
        el, a = geometry.az_el(vec + 0.001 * u, u, e, n)
        assert a == pytest.approx(az, abs=0.1) and 0 <= a < 360
    assert geometry.az_el(-u, u, e, n)[0] == pytest.approx(-90)
    # a vector marginally past unit length (float error) must not NaN
    assert np.isfinite(geometry.az_el(u * (1 + 1e-12), u, e, n)[0])


def test_earth_below_horizon_on_far_side_and_vectorised_shapes():
    el, az = geometry.earth_az_el(np.tile([1.0, 0, 0], (5, 1)), np.full(5, 3.84e8), 0.0, 180.0)
    assert (el < -89).all() and el.shape == az.shape == (5,)
    el2, _ = geometry.earth_az_el(np.array([1.0, 0, 0]), 3.84e8, 0.0, 0.0, h_m=5000.0)
    assert el2 == pytest.approx(90)  # height changes nothing at the sub-Earth point


# ------------------------------------------------------------------ polar projection
def test_pole_and_arrays():
    la, lo = polar.xy_to_lonlat(0.0, 0.0)
    assert la == -90 and lo == 0
    x, y = polar.lonlat_to_xy(np.array([-90.0]), np.array([77.0]))
    assert abs(x[0]) < 1e-9 and abs(y[0]) < 1e-9
    lat, lon = np.meshgrid(np.linspace(-89.9, -80, 7), np.linspace(-180, 179, 9))
    x, y = polar.lonlat_to_xy(lat, lon)
    la2, lo2 = polar.xy_to_lonlat(x, y)
    assert x.shape == lat.shape and np.allclose(la2, lat, atol=1e-9)
    assert np.allclose(np.cos(np.radians(lo2)), np.cos(np.radians(lon)), atol=1e-9)


def test_ray_direction_is_unit_and_wraps():
    dx, dy = polar.ray_direction(np.array([170.0, -170.0]), np.array([30.0, 400.0]))
    assert np.allclose(dx**2 + dy**2, 1)
    d1 = polar.ray_direction(10.0, 0.0)
    d2 = polar.ray_direction(10.0, 360.0)
    assert np.allclose(d1, d2)


def test_cell_centers_symmetric_row0_at_plus_y():
    x, y = polar.cell_centers(4, 100.0, 200.0)
    assert x[0, 0] == -150 and y[0, 0] == 150 and x.sum() == 0 and y.sum() == 0 and y[0, 0] > y[-1, 0]
    x1, y1 = polar.cell_centers(1, 400.0, 200.0)
    assert x1[0, 0] == 0 and y1[0, 0] == 0


# ------------------------------------------------------------------ config
def _cfg():
    return copy.deepcopy(config.load())


@pytest.mark.parametrize("mut", [
    lambda c: c.pop("power"), lambda c: c["power"].update(load_w=0), lambda c: c["power"].update(efficiency=-0.1),
    lambda c: c["grid"]["polar"].update(plot_m=1000), lambda c: c["grid"]["polar"].update(lat_min=-95.0),
    lambda c: c["price"]["range"].update(polar=0.4), lambda c: c["price"].update(rent_ratio=0),
    lambda c: c["stays"].append(0), lambda c: c["safety"].update(min_safe_frac=0),
    lambda c: c["weights"].update(safety=-1), lambda c: c["weights"].update({k: 0 for k in c["weights"]}),
    lambda c: c["moon"].update(radius_m=100), lambda c: c["analysis"].update(step_hours=0),
    lambda c: c["thermal"].update(swing_range_k=[300, 100]), lambda c: c["home_types"]["lander_pad"]["weights"].update(bogus=1),
])
def test_config_rejects_bad_values(mut):
    c = _cfg()
    mut(c)
    with pytest.raises((config.ConfigError, KeyError)):
        config.validate(c)


def test_config_custom_path_and_export(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(_cfg()))
    c = config.load(p)
    config.export(c, tmp_path / "sub" / "config.json", {"scarcity_viability_cutoff": 61.5})
    import json

    j = json.loads((tmp_path / "sub" / "config.json").read_text())
    assert j["computed"]["scarcity_viability_cutoff"] == 61.5 and j["power"]["load_w"] == c["power"]["load_w"]


# ------------------------------------------------------------------ contract helpers
def test_tile_index_boundaries_and_clipping():
    lo, hi = np.array([[0.0], [0.0]]), np.array([[16.0], [16.0]])
    t = contract.tile_index(np.array([0.0, 15.999, 16.0, 99.0, -5.0]), np.array([0.0, 0.0, 0.0, 0.0, 0.0]), lo, hi)
    assert list(t) == [0, 15, 15, 15, 0]
    t2 = contract.tile_index(np.array([0.0]), np.array([16.0]), lo, hi)
    assert t2[0] == 15 * 16  # y = hi clips to the last row


def test_write_cols_alignment_and_dtypes(tmp_path):
    n = 7
    cols = {name: np.arange(n).astype(dt) for name, dt, _ in contract.COLUMNS}
    contract.write_cols(tmp_path, cols, "global", ["a"], {"bounds": [0, 0, 1, 1], "projection": {"type": "lonlat"}})
    import json

    meta = json.loads((tmp_path / "cols.json").read_text())
    buf = (tmp_path / "cols.bin").read_bytes()
    assert all(c["offset"] % 4 == 0 for c in meta["columns"]) and len(buf) % 4 == 0
    c0 = meta["columns"][5]
    back = np.frombuffer(buf, np.dtype(c0["dtype"]).newbyteorder("<"), n, c0["offset"])
    assert np.array_equal(back, np.arange(n).astype(c0["dtype"]))
