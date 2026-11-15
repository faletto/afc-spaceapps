"""South polar stereographic (PGDA: sphere R=1,737,400 m, lat_origin -90, central meridian 0, k0=1).

x = rho sin(lon), y = rho cos(lon), rho = 2R tan(45deg + lat/2); +x/+y axes; lon east-positive.
Verified against the real DEMs (Mons Malapert high at -86/0.1E; Cabeus deep at 35.5W).
Azimuth: bearing alpha (0 = local north, 90 = east) maps to map angle lon + alpha measured from +y toward +x,
i.e. ray direction (sin(lon+alpha), cos(lon+alpha)). Conformal, so angles are preserved.
"""

import numpy as np

R_M = 1_737_400.0


def lonlat_to_xy(lat_deg, lon_deg):
    rho = 2 * R_M * np.tan(np.pi / 4 + np.radians(lat_deg) / 2)
    lo = np.radians(lon_deg)
    return rho * np.sin(lo), rho * np.cos(lo)


def xy_to_lonlat(x, y):
    """Returns (lat_deg, lon_deg). At the pole lon is 0 by convention."""
    rho = np.hypot(x, y)
    lat = -90.0 + np.degrees(2 * np.arctan(rho / (2 * R_M)))
    lon = np.degrees(np.arctan2(x, y))
    return lat, lon


def ray_direction(lon_deg, alpha_deg):
    """Unit map-plane direction (dx, dy) of the ray with bearing alpha from a site at longitude lon."""
    a = np.radians(np.asarray(lon_deg) + np.asarray(alpha_deg))
    return np.sin(a), np.cos(a)


def cell_centers(n: int, size_m: float, half_m: float):
    """x, y (m, +y up) of an n x n grid of cells covering [-half, half]^2; row 0 at +y."""
    c = (np.arange(n) + 0.5) * size_m - half_m
    return np.broadcast_to(c[None, :], (n, n)), np.broadcast_to(-c[:, None], (n, n))
