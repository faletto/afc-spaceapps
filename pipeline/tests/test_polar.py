import numpy as np
import pytest

from lunar_listings import polar


def test_roundtrip_and_radius():
    lat, lon = np.array([-85.0, -89.5, -87.3]), np.array([0.0, -129.0, 77.0])
    x, y = polar.lonlat_to_xy(lat, lon)
    la2, lo2 = polar.xy_to_lonlat(x, y)
    assert np.allclose(la2, lat) and np.allclose(lo2, lon)
    assert np.hypot(*polar.lonlat_to_xy(-85.0, 10.0)) == pytest.approx(151_800, abs=300)


def test_ray_direction_matches_local_north_east():
    lat, lon = -87.0, 40.0
    x0, y0 = polar.lonlat_to_xy(lat, lon)
    dx, dy = polar.ray_direction(lon, 0)  # north: latitude grows, longitude unchanged
    la, lo = polar.xy_to_lonlat(x0 + 1000 * dx, y0 + 1000 * dy)
    assert la > lat and abs(lo - lon) < 1e-9
    dx, dy = polar.ray_direction(lon, 90)  # east: longitude grows, latitude ~unchanged (2nd order)
    la, lo = polar.xy_to_lonlat(x0 + 1000 * dx, y0 + 1000 * dy)
    assert lo > lon and abs(la - lat) < 1e-3
