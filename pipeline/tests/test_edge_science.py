"""Edge cases: visibility/best windows, terrain, horizons, scoring, pricing/rent, land, blurbs."""

import copy
import itertools
import warnings

import numpy as np
import pytest

from lunar_listings import blurbs, config, ephemeris, horizons, land, pricing, scoring, terrain, visibility

CFG = config.load()


@pytest.fixture(scope="module")
def eph():
    return ephemeris.load()


# ------------------------------------------------------------------ visibility
def test_wall_all_around_never_sunlit_and_horizon_below_always_lit(eph):
    k = visibility.site_stats(
        np.array([0.0, 0.0]),
        np.array([0.0, 0.0]),
        np.vstack([np.full(180, 95.0), np.full(180, -60.0)]),
        eph,
        CFG,
    )  # 95 deg: even the zenith Sun at the equator is hidden
    assert k["sunlit_frac"][0] == 0 and k["longest_dark_h"][0] == 8784 and k["energy_wh_m2_day"][0] == 0
    assert (
        k["temp_max_k"][0] == 40 and k["temp_min_k"][0] == 40 and k["earth_frac"][0] == 0
    )  # PSR floor, walled-in
    # horizon at -60 deg: the Sun is hidden only while below -60 deg, i.e. 30/360 of the 708 h day around local midnight
    assert k["longest_dark_h"][1] == pytest.approx(708 * 60 / 360, abs=8) and 0.8 < k["sunlit_frac"][1] < 0.9


def test_modes_and_panel_config_change_results(eph):
    base = visibility.site_stats(np.array([30.0]), np.array([10.0]), np.zeros((1, 180)), eph, CFG)
    limb = lambda cfg: visibility.site_stats(
        np.array([30.0]), np.array([80.0]), np.zeros((1, 180)), eph, cfg
    )["earth_frac"][0]
    c = copy.deepcopy(CFG)
    c["comms"].update(mode="absolute", cutoff_deg=20.0)
    assert limb(c) < limb(
        CFG
    )  # near the limb a 20 deg cutoff costs contact; a 1 deg margin over flat terrain does not
    c = copy.deepcopy(CFG)
    c["power"]["panel"] = "horizontal"
    assert (
        visibility.site_stats(np.array([30.0]), np.array([10.0]), np.zeros((1, 180)), eph, c)[
            "energy_wh_m2_day"
        ][0]
        < base["energy_wh_m2_day"][0]
    )
    c = copy.deepcopy(CFG)
    c["power"]["sunlit_threshold"] = 0.99
    assert (
        visibility.site_stats(np.array([30.0]), np.array([10.0]), np.zeros((1, 180)), eph, c)["sunlit_frac"][
            0
        ]
        < base["sunlit_frac"][0]
    )


def test_horizon_resolution_independent_and_wraparound(eph):
    flat = visibility.site_stats(np.array([-86.0]), np.array([20.0]), np.full((1, 180), 1.0), eph, CFG)
    same = visibility.site_stats(
        np.array([-86.0]), np.array([20.0]), np.full((1, 90), 1.0), eph, CFG
    )  # coarser az grid
    assert flat["sunlit_frac"][0] == pytest.approx(same["sunlit_frac"][0])
    spike = np.zeros((1, 180))
    spike[0, 179] = 30.0  # last sample interpolates with sample 0 across north (circular)
    r = visibility.site_stats_ref(
        -86.0,
        20.0,
        spike[0],
        eph["sun_xyz"],
        eph["earth_xyz"],
        eph["earth_dist_m"],
        eph["tsi"],
        eph["r_sun_km"],
        CFG,
        visibility.month_of_hour(2028, 8784),
    )
    k = visibility.site_stats(np.array([-86.0]), np.array([20.0]), spike, eph, CFG)
    assert k["sunlit_frac"][0] == pytest.approx(r["sunlit_frac"])


def test_one_hour_and_short_windows(eph):
    w = {k: v[100:101] for k, v in eph.items()}
    k = visibility.site_stats(np.array([0.0]), np.array([0.0]), np.zeros((1, 180)), w, CFG, start_hour=100)
    assert k["sunlit_frac"][0] in (0.0, 1.0) and np.isnan(k["monthly_sunlit"][0]).sum() == 11


def test_month_of_hour_calendar():
    m = visibility.month_of_hour(2028, 8784)
    assert (
        m[0] == 0
        and m[-1] == 11
        and np.bincount(m).tolist() == [24 * d for d in (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)]
    )
    assert visibility.month_of_hour(2028, 2, start_hour=31 * 24 - 1).tolist() == [0, 1]


def test_runs_edge_cases():
    assert visibility.runs_of_false(np.array([], bool)) == []
    assert visibility.runs_of_false(np.ones(5, bool)) == []
    assert visibility.runs_of_false(np.zeros(5, bool)) == [(0, 5)]
    assert visibility.runs_of_false(np.array([0, 1, 0], bool)) == [(0, 1), (2, 1)]


def test_best_window_edges():
    ones, zeros = np.ones((1, 24 * 40), bool), np.zeros((1, 24 * 40), bool)
    assert visibility.best_window(ones, 14)[0][0] == 0
    assert visibility.best_window(zeros, 14)[0][0] == 14 * 24
    h, d = visibility.best_window(zeros, 400)  # stay longer than the window -> the whole window
    assert h[0] == 24 * 40 and d[0] == 1
    assert visibility.best_window_ref(zeros[0], 400) == (24 * 40, 1)
    with pytest.raises(ValueError):
        visibility.best_window(ones, 0)
    m = np.ones((1, 24 * 40), bool)
    m[0, 24 * 10 : 24 * 20] = (
        False  # a 10-day night; a 14-day stay can avoid it only by starting after day 20
    )
    h, d = visibility.best_window(m, 14)
    assert h[0] == 0 and d[0] >= 21 or h[0] == 0 and d[0] == 1  # either side of the night
    assert visibility.best_window(m, 14) == tuple(np.array([x]) for x in visibility.best_window_ref(m[0], 14))


# ------------------------------------------------------------------ terrain
def test_resample_all_nan_block_and_nodata():
    a = np.full((4, 4), -32768, np.float32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        out = terrain.resample_block_mean(a, (2, 2), nodata=-32768)
    assert np.isnan(out).all()


def test_plot_stats_nan_pixels_do_not_poison_block():
    n = terrain.CELLS_PER_DEG
    dem = np.zeros((n, n))
    sl = np.full((n, n), 5.0, np.float32)
    sl[0, :4] = np.nan
    st = terrain.global_plot_stats(dem, sl, 8.0)
    assert st["slope_mean_deg"][0, 0] == pytest.approx(5.0) and st["safe_area_frac"][0, 0] == 1.0
    sl[:] = 8.0  # equality is NOT safe (strict <)
    assert terrain.global_plot_stats(dem, sl, 8.0)["safe_area_frac"][0, 0] == 0.0


def test_slope_poles_and_antimeridian_wrap():
    dem = np.zeros((64, 128))
    dem[:, 0], dem[:, -1] = 100.0, 100.0  # a ridge straddling lon = +-180 must stay a ridge (np.roll wrap)
    s = terrain.slope_deg_lonlat(dem, 180 / 64)
    assert np.isfinite(s).all() and s[32, 1] > 0 and s[32, 126] > 0 and s[0].max() < 90


def test_hazard_clamps_and_norm_degenerate():
    cfg = {"safety": {"slope_p90_range": [0, 30], "roughness_range_m": [0, 50], "relief_range_m": [0, 2000]}}
    assert terrain.hazard_score(-5, -5, -5, cfg) == 0 and terrain.hazard_score(1e9, 1e9, 1e9, cfg) == 1
    assert terrain.norm(np.array([-1, 0.5, 2]), (0, 1)).tolist() == [0, 0.5, 1]


# ------------------------------------------------------------------ horizons
def _flat(h=0.0, near_half=10_000.0, far_half=40_000.0):
    def g(half, res):
        n = round(2 * half / res)
        return np.full((n, n), h, np.float32)

    return horizons.Dems(g(near_half, 20.0), near_half, 20.0, g(far_half, 80.0), far_half, 80.0)


def test_observer_outside_or_nan_dem_gives_nan_row_not_crash():
    d = _flat()
    out = horizons.compute(np.array([500_000.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0]), d, CFG)
    assert np.isnan(out[0]).all() and np.isfinite(out[1]).all()
    d.near[:] = np.nan
    d.far[:] = np.nan
    assert np.isnan(horizons.compute(np.array([0.0]), np.array([0.0]), np.array([0.0]), d, CFG)).all()


def test_rays_leaving_raster_are_finite_and_empty_input():
    d = _flat()
    out = horizons.compute(
        np.array([39_000.0]), np.array([39_000.0]), np.array([45.0]), d, CFG
    )  # near the far-DEM corner
    assert np.isfinite(out).all() and out.shape == (1, 180)
    assert horizons.compute(np.array([]), np.array([]), np.array([]), d, CFG).shape == (0, 180)


def test_height_offset_does_not_change_flat_horizon_and_wall_angle_bounded():
    a = horizons.compute(np.array([0.0]), np.array([0.0]), np.array([0.0]), _flat(0.0), CFG)
    b = horizons.compute(np.array([0.0]), np.array([0.0]), np.array([0.0]), _flat(2500.0), CFG)
    assert np.allclose(a, b, atol=1e-4)
    wall = _flat()
    wall.near[:, 520:] = 30_000.0  # a 30 km cliff 120 m east of the observer is not a valid horizon > 90 deg
    assert horizons.compute(np.array([0.0]), np.array([0.0]), np.array([0.0]), wall, CFG).max() <= 90.0


def test_quantize_edge_values():
    q = horizons.quantize(np.array([np.nan, -6.0, -6.09, 34.8, 34.9, 1e9, -1e9, np.inf]))
    assert q.dtype == np.uint8 and q.tolist() == [0, 0, 0, 255, 255, 255, 0, 255]
    assert horizons.dequantize(np.array([0, 255], np.uint8)).tolist() == pytest.approx([-6.0, 34.8], abs=1e-4)


# ------------------------------------------------------------------ scoring
def test_subscores_stay_in_unit_interval_for_extreme_inputs():
    n = 6
    t = {
        "hazard_score": np.array([0, 1, 0.5, 0, 1, 0.3]),
        "energy_wh_m2_day": np.array([0, 1e9, 1e4, 0, 3e4, -50.0]),
        "longest_dark_h": np.array([0, 0, 8784, 8784, 1e9, 10.0]),
        "earth_frac": np.array([0, 1, 0.5, 0, 1, 1.0]),
        "longest_blackout_h": np.array([0, 8784, 0, 8784, 5, 0.0]),
        "temp_min_k": np.array([40, 400, 95, 40, 120, 95.0]),
        "temp_max_k": np.array([40, 400, 390, 40, 100, 390.0]),
        "landmark_score": np.array([0, 1, 0.2, 0, 1, 0.0]),
        "ice_km": np.array([0, 100, 5, 50, 0, 1e9]),
    }
    s = scoring.subscores(t, CFG, polar=True)
    for k, v in s.items():
        assert v.shape == (n,) and (v >= 0).all() and (v <= 1).all() and np.isfinite(v).all(), k
    assert scoring.subscores(t, CFG)["ice"].sum() == 0  # Moon-wide: ice score is 0
    v = scoring.viability(s, np.array([True, True, False, False, True, False]), CFG)
    assert ((0 <= v) & (v <= 100)).all() and (v[[2, 3, 5]] <= 10).all()


def test_viability_weights_override_and_named_scores_range():
    s = {k: np.array([0.5]) for k in ("safety", "power", "comms", "thermal", "landmark", "ice")}
    s["power"] = np.array([1.0])
    only_power = scoring.viability(s, np.array([True]), CFG, weights={"power": 1.0})
    assert only_power[0] == pytest.approx(100)
    ns = scoring.named_scores({k: np.array([0.0, 1.0, 0.505]) for k in s})
    assert all(
        v.dtype == np.uint8
        and v.tolist() == [0, 100, 50 + 1 - 1 + 1 if False else 50]
        or v.tolist() == [0, 100, 51]
        for v in ns.values()
    )


def test_thermal_hazard_extremes_and_penalty_vectors():
    assert scoring.thermal_hazard(120, 120, CFG) == 0  # warm floor, no swing
    assert scoring.thermal_hazard(40, 340, CFG) == 1  # coldest, biggest swing
    assert np.allclose(scoring.penalty(np.array([0, 120, 1e12]), 120, 2), [1, 0.5, 0], atol=1e-12)
    assert scoring.power_score(np.array([0.0, 3e4]), np.array([8784, 8784]), CFG).max() < 0.1


# ------------------------------------------------------------------ pricing and rent
@pytest.mark.parametrize("v", [0, 100, 50.5])
def test_price_is_finite_positive_and_increasing(v):
    p = pricing.price_usd(v, CFG)
    assert np.isfinite(p) and p >= 5000 and pricing.price_usd(v + 0.1, CFG) > p


def test_scarcity_cutoff_inclusive_and_constant_arrays():
    v = np.full(100, 40.0)
    c = pricing.scarcity_cutoff(v, CFG)
    assert c == 40.0 and pricing.price_usd(40.0, CFG, cutoff=c) == pytest.approx(
        1.3 * pricing.price_usd(40.0, CFG)
    )  # >= is inclusive
    assert pricing.price_usd(39.999, CFG, cutoff=c) == pricing.price_usd(39.999, CFG)


@pytest.mark.parametrize(
    "x,s",
    [
        (0, "$0"),
        (999, "$999"),
        (999.4, "$999"),
        (1000, "$1K"),
        (999_499, "$999K"),
        (999_500, "$1M"),
        (4_200_000, "$4.2M"),
        (12_340_000, "$12.3M"),
        (123_400_000, "$123M"),
        (1.5e9, "$1.5B"),
        (1e12, "$1000B"),
    ],
)
def test_format_usd_table(x, s):
    assert pricing.format_usd(x) == s


def test_badges_priority_and_limit():
    f = {"off_market": 1, "hot_property": 1, "peak_of_light": 1, "earth_view": 1, "price_cut": 1}
    assert pricing.badges(f) == ["off_market", "hot_property"] and pricing.badges(f, 3)[2] == "peak_of_light"
    assert pricing.badges({}) == [] and pricing.badges({"price_cut": 1}, 0) == []


def _site(**kw):
    s = {
        "lat": -89.0,
        "lon": 10.0,
        "horizon_deg": np.full(180, 0.5),
        "hazard_score": 0.3,
        "landmark_score": 0.0,
        "landing_safe": True,
        "premium": 0.0,
        "ice_km": 1.0,
    }
    s.update(kw)
    return s


def test_rent_edge_windows_and_flags(eph):
    last = pricing.rent_for_stay(_site(), eph, CFG, 60.0, 366, 1)
    assert last["stay_hours"] == 24 and np.isfinite(last["rent_per_month"])
    first_year = pricing.rent_for_stay(_site(), eph, CFG, 60.0, 1, 10_000)  # absurd stay: clipped to the year
    assert first_year["stay_hours"] == 8784
    off = pricing.rent_for_stay(_site(landing_safe=False), eph, CFG, 60.0, 1, 366)
    assert off["viability_stay"] <= 10 and off["rent_per_month"] < first_year["rent_per_month"]
    prem = pricing.rent_for_stay(_site(premium=0.25), eph, CFG, 60.0, 1, 366)
    assert prem["rent_per_month"] == pytest.approx(1.25 * first_year["rent_per_month"])
    moon = pricing.rent_for_stay(_site(ice_km=None), eph, CFG, 60.0, 1, 366)
    assert np.isfinite(moon["rent_per_month"])
    for bad in (0, -3, 367):
        with pytest.raises(ValueError):
            pricing.rent_for_stay(_site(), eph, CFG, 60.0, bad, 14)


def test_total_stay_cost_consistent(eph):
    r = pricing.rent_for_stay(_site(), eph, CFG, 60.0, 50, 30)
    assert r["total_stay"] == pytest.approx(r["rent_per_month"] * 30 / (365.25 / 12), rel=1e-9)


# ------------------------------------------------------------------ land
def test_great_circle_symmetry_and_triangle():
    rng = np.random.default_rng(5)
    la, lo = rng.uniform(-90, 90, (3, 20)), rng.uniform(-180, 180, (3, 20))
    d = land.great_circle_km
    assert np.allclose(d(la[0], lo[0], la[1], lo[1]), d(la[1], lo[1], la[0], lo[0]))
    assert (
        d(la[0], lo[0], la[2], lo[2]) <= d(la[0], lo[0], la[1], lo[1]) + d(la[1], lo[1], la[2], lo[2]) + 1e-6
    ).all()
    assert d(0, 179.5, 0, -179.5) == pytest.approx(d(0, 0, 0, 1))


def test_landmark_score_ranges_and_radius():
    lm = {
        "name": np.array(["A", "B"]),
        "type": np.array(["x", "x"]),
        "lat": np.array([0.0, 60.0]),
        "lon": np.array([0.0, 0.0]),
        "fame_class": np.array(["apollo_artemis", "other"]),
    }
    s, near = land.landmark_score_and_nearby(np.array([0.0, 30.0, -80.0]), np.array([0.0, 0.0, 0.0]), lm, CFG)
    assert s[0] == pytest.approx(1.0) and 0 < s[1] < s[0] and s[2] < 1e-6
    assert (
        near[0, 0] == 0 and near[0, 1] == -1 and (near[2] == -1).all()
    )  # beyond radius -> -1, never a wrong index
    idx, km = land.nearest_landmark(np.array([59.0]), np.array([0.0]), lm)
    assert idx[0] == 1 and km[0] == pytest.approx(land.R_KM * np.radians(1), rel=1e-3)
    a = land.apollo_distance_km(np.array([0.0, 60.0]), np.array([0.0, 0.0]), lm)
    assert a[0] == 0 and a[1] == pytest.approx(land.R_KM * np.radians(60), rel=1e-6)


def test_land_type_priority_matrix_and_polar_flag():
    base = {
        "sunlit_frac": np.array([0.5]),
        "lat": np.array([-87.0]),
        "lon": np.array([120.0]),
        "elev_mean_m": np.array([0.0]),
        "tpi_hi": np.array([0.0]),
        "tpi_lo": np.array([0.0]),
    }
    f = lambda polar, **kw: land.LAND_TYPES[
        land.land_type(
            *(
                ({**base, **{k: np.array([v]) for k, v in kw.items()}})[k]
                for k in ("sunlit_frac", "lat", "lon", "elev_mean_m", "tpi_hi", "tpi_lo")
            ),
            CFG,
            polar,
            median_ref=0.0,
        )[0]
    ]
    assert f(False) == "far_side" and f(True) == "highlands"
    assert (
        f(True, sunlit_frac=0.005) == "psr"
        and f(True, sunlit_frac=0.9) == "peak_of_light"
        and f(False, sunlit_frac=0.9) == "far_side"
    )
    assert f(True, elev_mean_m=-1001.0) == "mare" and f(True, elev_mean_m=-999.0) == "highlands"
    assert f(True, tpi_hi=400.0) == "crater_rim" and f(True, tpi_lo=-400.0) == "crater_floor"
    assert f(True, tpi_hi=400.0, tpi_lo=-500.0) == "crater_floor"  # larger magnitude wins
    assert f(True, sunlit_frac=0.9, tpi_hi=400.0) == "peak_of_light"


# ------------------------------------------------------------------ blurbs
def test_blurbs_total_function_over_a_fact_grid():
    names = land.LAND_TYPES
    n = 0
    for sun, earth, lt, ice, dark, polar, safe, nearby, apollo in itertools.product(
        (0.0, 0.3, 0.75, 1.0),
        (0.0, 0.5, 0.97),
        names,
        (0.3, 3.0, 99.0),
        (0.0, 500.0),
        (0, 1),
        (0, 1),
        ("", "Tycho"),
        (10.0, 999.0),
    ):
        f = {
            "sunlit": sun,
            "earth": earth,
            "land": lt,
            "ice_km": ice,
            "tmin_k": 95.0,
            "tmax_k": 390.0 if sun > 0.5 else 80.0,
            "slope_deg": 4.0,
            "viability": 40.0,
            "safe": safe,
            "dark_h": dark,
            "polar": polar,
            "apollo_km": apollo,
            "nearby": nearby,
        }
        b = blurbs.blurb(f"G-{n:03d}-001", f)
        assert b and "{" not in b and "}" not in b and b[0].isupper()
        n += 1
    assert n > 1000


def test_blurb_hash_is_stable_across_runs():
    assert (
        blurbs.pick("SP-0032-0154", 7)
        == blurbs.pick("SP-0032-0154", 7)
        == int.from_bytes(__import__("hashlib").sha256(b"SP-0032-0154").digest()[:4], "big") % 7
    )
    assert {blurbs.pick(f"X{i}", 5) for i in range(100)} == {0, 1, 2, 3, 4}


def test_why_ties_and_empty():
    assert blurbs.why({}) == "Priced as a typical lunar lot"
    assert blurbs.why({"power": 0.5, "comms": 0.5}).startswith("Priced up for")
    assert "down for" in blurbs.why({"power": 0.0, "safety": 0.0})
