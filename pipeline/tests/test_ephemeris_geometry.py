import numpy as np
import pytest

from lunar_listings import ephemeris, geometry

SAMPLE = """Target pole/equ : MOON_ME                         {%s-longitude positive}
 Date__(UT)__HR:MN, , , ObsSub-LON, ObsSub-LAT,  SunSub-LON, SunSub-LAT,                r,       rdot,             delta,     deldot,
*****
$$SOE
 2028-Jan-01 00:00, , , 10.0,  -2.0,  100.0, -0.5,  1.468E+08,  0.5,  4.05E+05,  0.0,
$$EOE
"""


def test_east_and_west_sign():
    e = ephemeris.parse_horizons(SAMPLE % "East")[0]
    w = ephemeris.parse_horizons(SAMPLE % "West")[0]
    assert e[1] == 10.0 and e[3] == 100.0
    assert w[1] == 350.0 and w[3] == 260.0


def test_missing_sign_line_fails():
    with pytest.raises(ValueError):
        ephemeris.parse_horizons(SAMPLE.replace("{%s-longitude positive}", "") )


@pytest.fixture(scope="module")
def eph():
    return ephemeris.load()


def test_ephemeris_ranges(eph):
    assert eph["sun_xyz"].shape == (8784, 3)
    assert np.allclose(np.linalg.norm(eph["sun_xyz"], axis=1), 1)
    assert 1300 <= eph["tsi"].min() and eph["tsi"].max() <= 1420  # spec says 1412; 2028 perihelion gives ~1413
    assert 356e6 < eph["earth_dist_m"].min() and eph["earth_dist_m"].max() < 407e6


def test_subsolar_point_is_zenith(eph):
    t = 1000
    lon = np.degrees(np.arctan2(eph["sun_xyz"][t, 1], eph["sun_xyz"][t, 0]))
    lat = np.degrees(np.arcsin(eph["sun_xyz"][t, 2]))
    el, _ = geometry.sun_az_el(eph["sun_xyz"][t], lat, lon)
    assert el == pytest.approx(90, abs=1e-6)


def test_earth_parallax_and_frame():
    # Earth straight above sub-Earth point: elevation 90 there
    u, e, n = geometry.enu_frame(0, 0)
    d = np.array([1.0, 0, 0])
    el, _ = geometry.az_el(d, u, e, n)
    assert el == pytest.approx(90)
    # Direction due east at the horizon: az 90, el 0; due north: az 0
    assert geometry.az_el(e, u, e, n) == (pytest.approx(0), pytest.approx(90))
    assert geometry.az_el(n, u, e, n)[1] == pytest.approx(0)
    # Parallax: Earth at sub-Earth point is 90 deg for any site on the axis; 90deg away from it,
    # Earth sits ~0.26 deg BELOW the horizon (site displaced toward it) (R/delta rad = 0.2455 deg)
    el, _ = geometry.earth_az_el(np.array([1.0, 0, 0]), 384.4e6, 0, 90)
    assert el == pytest.approx(-np.degrees(geometry.R_MOON_M / 384.4e6), abs=0.01)


def test_pole_defined():
    el, az = geometry.az_el(np.array([0.0, 0, 1]), *geometry.enu_frame(90, 0))
    assert el == pytest.approx(90) and np.isfinite(az)
