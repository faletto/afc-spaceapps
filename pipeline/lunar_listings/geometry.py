"""Local geometry (spec §3.3). Shared formulas -> golden vectors for the TypeScript mirror.

Pole convention: at |lat| = 90 the north vector n is undefined. We use the limit along lon = 0 (so
n = (-sinφ, 0, cosφ) at the pole, with e = (0, 1, 0)); azimuth at the pole is therefore
measured from the lon=0 meridian direction. Map grid-north azimuth for polar tiles is applied in the
polar export (P4). Validation compares elevations only at the pole.
"""

import numpy as np

R_MOON_M = 1_737_400.0


def enu_frame(lat_deg: float, lon_deg: float):
    """Return (u, e, n) unit vectors in the Moon-fixed frame."""
    la, lo = np.radians(lat_deg), np.radians(lon_deg)
    u = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    e = np.array([-np.sin(lo), np.cos(lo), 0.0])
    n = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])
    return u, e, n  # at the poles cos(la)=0 and lon is used as given: well-defined limit


def az_el(d, u, e, n):
    """Elevation (deg) and azimuth (deg, 0=N, 90=E) of direction(s) d (..., 3)."""
    d = np.asarray(d)
    el = np.degrees(np.arcsin(np.clip(d @ u, -1, 1)))
    az = np.degrees(np.arctan2(d @ e, d @ n)) % 360
    return el, az


def sun_az_el(sun_xyz, lat_deg, lon_deg):
    return az_el(sun_xyz, *enu_frame(lat_deg, lon_deg))


def earth_az_el(earth_xyz, earth_dist_m, lat_deg, lon_deg, h_m=0.0, R=R_MOON_M):
    """Earth direction including parallax (site offset from Moon centre)."""
    u, e, n = enu_frame(lat_deg, lon_deg)
    d = earth_xyz * np.asarray(earth_dist_m)[..., None] - (R + h_m) * u
    d = d / np.linalg.norm(d, axis=-1, keepdims=True)
    return az_el(d, u, e, n)
