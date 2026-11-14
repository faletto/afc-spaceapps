"""Per-site, per-hour Sun/Earth visibility and annual statistics (spec §3.6-3.7).

`site_stats_ref` is the pure-NumPy reference (also the source of golden vectors); `site_stats` is the
Numba kernel. Both take the same inputs and must agree (tests).

Horizon convention: `horizon_deg[site, k]` = terrain elevation angle at azimuth k * 360/naz (0 = N, 90 = E),
circularly linearly interpolated. Pass zeros for the Moon-wide tier (m == 0).
"""
import numpy as np
from numba import njit, prange

AU_KM = 149_597_870.7
SIGMA = 5.670e-8
RHO_1AU_DEG = 0.2666
MONTH_OF_HOUR_DEFAULT_YEAR = 2028


def month_of_hour(year: int, n: int) -> np.ndarray:
    t = np.datetime64(f"{year}-01-01T00") + np.arange(n).astype("timedelta64[h]")
    return (t.astype("datetime64[M]").astype(int) % 12).astype(np.int64)


def _frames(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    u = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)
    e = np.stack([-np.sin(lo), np.cos(lo), np.zeros_like(lo)], -1)
    n = np.stack([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)], -1)
    return u, e, n


def _runs_longest(b):
    """Longest run of True in a 1-D bool array."""
    best = cur = 0
    for v in b:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def site_stats_ref(lat, lon, horizon_deg, sun, earth, dist_m, tsi, r_sun_km, cfg, month, R=1_737_400.0):
    """Reference for ONE site. Returns dict of scalars/arrays (see KEYS)."""
    pw, cm, th = cfg["power"], cfg["comms"], cfg["thermal"]
    u, e, n = (x[0] for x in _frames(np.array([lat]), np.array([lon])))
    naz = len(horizon_deg)
    hz = np.asarray(horizon_deg, float)

    def m_at(az):
        f = (az / (360.0 / naz)) % naz
        i0 = np.floor(f).astype(int) % naz
        t = f - np.floor(f)
        return hz[i0] * (1 - t) + hz[(i0 + 1) % naz] * t

    es = np.degrees(np.arcsin(np.clip(sun @ u, -1, 1)))
    asun = np.degrees(np.arctan2(sun @ e, sun @ n)) % 360
    d = earth * dist_m[:, None] - R * u
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    ee = np.degrees(np.arcsin(np.clip(d @ u, -1, 1)))
    aearth = np.degrees(np.arctan2(d @ e, d @ n)) % 360
    rho = RHO_1AU_DEG / (r_sun_km / AU_KM)
    x = np.clip((es - m_at(asun)) / rho, -1, 1)
    f_sun = (np.arccos(-x) + x * np.sqrt(1 - x * x)) / np.pi
    sunlit = f_sun > pw["sunlit_threshold"]
    me = m_at(aearth)
    if cm["mode"] == "terrain_margin":
        earth_ok = ee >= me + cm["margin_deg"]
    else:
        earth_ok = (ee >= cm["cutoff_deg"]) & (ee >= me)
    panel = np.cos(np.radians(es)) if pw["panel"] == "vertical_tracking" else np.maximum(0, np.sin(np.radians(es)))
    days = len(es) / 24.0
    energy = (tsi * f_sun * panel * pw.get("area_m2_norm", 1.0)).sum() / days  # Wh/m2/day (1 h steps)
    fh = tsi * f_sun * np.maximum(0, np.sin(np.radians(es)))
    teq = (np.maximum(0, (1 - th["albedo"]) * fh / (th["emissivity"] * SIGMA))) ** 0.25
    floor = th["psr_floor_k"] if sunlit.mean() == 0 else th["floor_k"]
    t = np.maximum(teq, floor)
    return {
        "sunlit_frac": sunlit.mean(), "longest_dark_h": _runs_longest(~sunlit),
        "longest_light_h": _runs_longest(sunlit), "energy_wh_m2_day": energy,
        "earth_frac": earth_ok.mean(), "longest_blackout_h": _runs_longest(~earth_ok),
        "mean_earth_el": ee.mean(), "temp_min_k": t.min(), "temp_mean_k": t.mean(), "temp_max_k": t.max(),
        "monthly_sunlit": np.array([sunlit[month == k].mean() if (month == k).any() else np.nan for k in range(12)]),
        "monthly_earth": np.array([earth_ok[month == k].mean() if (month == k).any() else np.nan for k in range(12)]),
    }


@njit(cache=True)
def _longest(b, want):
    best = cur = 0
    for v in b:
        if v == want:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


@njit(cache=True, parallel=True)
def _kernel(lat, lon, hz, sun, earth, dist, tsi, rsun, month, vertical, thr, use_margin, margin, cutoff,
            albedo, emis, floor_k, psr_k, R, out, mon_s, mon_e):
    ns, nt, naz = lat.shape[0], sun.shape[0], hz.shape[1]
    step = 360.0 / naz
    counts = np.zeros(12)
    for t in range(nt):
        counts[month[t]] += 1
    for i in prange(ns):
        la, lo = np.radians(lat[i]), np.radians(lon[i])
        u = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
        e = np.array([-np.sin(lo), np.cos(lo), 0.0])
        n = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])
        sunlit = np.zeros(nt, np.bool_)
        eok = np.zeros(nt, np.bool_)
        n_sun = n_e = 0
        energy = 0.0
        ee_sum = 0.0
        tsum95, tsum40 = 0.0, 0.0
        tmin95, tmin40, tmax95, tmax40 = 1e9, 1e9, 0.0, 0.0
        for t in range(nt):
            es = np.degrees(np.arcsin(min(1.0, max(-1.0, sun[t, 0] * u[0] + sun[t, 1] * u[1] + sun[t, 2] * u[2]))))
            asun = np.degrees(np.arctan2(sun[t] @ e, sun[t] @ n)) % 360.0
            dx = earth[t, 0] * dist[t] - R * u[0]
            dy = earth[t, 1] * dist[t] - R * u[1]
            dz = earth[t, 2] * dist[t] - R * u[2]
            nrm = np.sqrt(dx * dx + dy * dy + dz * dz)
            dx, dy, dz = dx / nrm, dy / nrm, dz / nrm
            ee = np.degrees(np.arcsin(min(1.0, max(-1.0, dx * u[0] + dy * u[1] + dz * u[2]))))
            aea = np.degrees(np.arctan2(dx * e[0] + dy * e[1] + dz * e[2], dx * n[0] + dy * n[1] + dz * n[2])) % 360.0
            # horizon interpolation
            f = (asun / step) % naz
            i0 = int(np.floor(f)) % naz
            tt = f - np.floor(f)
            ms = hz[i, i0] * (1 - tt) + hz[i, (i0 + 1) % naz] * tt
            f = (aea / step) % naz
            i0 = int(np.floor(f)) % naz
            tt = f - np.floor(f)
            me = hz[i, i0] * (1 - tt) + hz[i, (i0 + 1) % naz] * tt
            rho = 0.2666 / (rsun[t] / 149597870.7)
            x = min(1.0, max(-1.0, (es - ms) / rho))
            fs = (np.arccos(-x) + x * np.sqrt(1 - x * x)) / np.pi
            sunlit[t] = fs > thr
            if use_margin:
                eok[t] = ee >= me + margin
            else:
                eok[t] = (ee >= cutoff) and (ee >= me)
            n_sun += sunlit[t]
            n_e += eok[t]
            ee_sum += ee
            if vertical:
                pf = np.cos(np.radians(es))
            else:
                pf = max(0.0, np.sin(np.radians(es)))
            energy += tsi[t] * fs * pf
            fh = tsi[t] * fs * max(0.0, np.sin(np.radians(es)))
            teq = (max(0.0, (1 - albedo) * fh / (emis * 5.670e-8))) ** 0.25
            t95, t40 = max(teq, floor_k), max(teq, psr_k)
            tsum95 += t95
            tsum40 += t40
            tmin95, tmax95 = min(tmin95, t95), max(tmax95, t95)
            tmin40, tmax40 = min(tmin40, t40), max(tmax40, t40)
            if sunlit[t]:
                mon_s[i, month[t]] += 1.0
            if eok[t]:
                mon_e[i, month[t]] += 1.0
        psr = n_sun == 0
        out[i, 0] = n_sun / nt
        out[i, 1] = _longest(sunlit, False)
        out[i, 2] = _longest(sunlit, True)
        out[i, 3] = energy / (nt / 24.0)
        out[i, 4] = n_e / nt
        out[i, 5] = _longest(eok, False)
        out[i, 6] = ee_sum / nt
        out[i, 7] = tmin40 if psr else tmin95
        out[i, 8] = (tsum40 if psr else tsum95) / nt
        out[i, 9] = tmax40 if psr else tmax95
        for k in range(12):
            mon_s[i, k] = mon_s[i, k] / counts[k] if counts[k] > 0 else np.nan
            mon_e[i, k] = mon_e[i, k] / counts[k] if counts[k] > 0 else np.nan


KEYS = ["sunlit_frac", "longest_dark_h", "longest_light_h", "energy_wh_m2_day", "earth_frac",
        "longest_blackout_h", "mean_earth_el", "temp_min_k", "temp_mean_k", "temp_max_k"]


def site_stats(lat, lon, horizon_deg, eph, cfg, year=2028, R=1_737_400.0):
    """Numba kernel over many sites. eph: dict with sun_xyz, earth_xyz, earth_dist_m, tsi, r_sun_km."""
    lat, lon = np.ascontiguousarray(lat, float), np.ascontiguousarray(lon, float)
    hz = np.ascontiguousarray(horizon_deg, float)
    pw, cm, th = cfg["power"], cfg["comms"], cfg["thermal"]
    nt = len(eph["tsi"])
    out = np.zeros((len(lat), 10))
    ms, me = np.zeros((len(lat), 12)), np.zeros((len(lat), 12))
    _kernel(lat, lon, hz, np.ascontiguousarray(eph["sun_xyz"]), np.ascontiguousarray(eph["earth_xyz"]),
            np.ascontiguousarray(eph["earth_dist_m"]), np.ascontiguousarray(eph["tsi"]),
            np.ascontiguousarray(eph["r_sun_km"]), month_of_hour(year, nt), pw["panel"] == "vertical_tracking",
            pw["sunlit_threshold"], cm["mode"] == "terrain_margin", cm["margin_deg"], cm["cutoff_deg"],
            th["albedo"], th["emissivity"], th["floor_k"], th["psr_floor_k"], R, out, ms, me)
    res = {k: out[:, j] for j, k in enumerate(KEYS)}
    res["monthly_sunlit"], res["monthly_earth"] = ms, me
    return res
