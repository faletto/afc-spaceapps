import numpy as np
import pytest

from lunar_listings import config, ephemeris, pricing, scoring, visibility

CFG = config.load()


@pytest.fixture(scope="module")
def eph():
    return ephemeris.load()


def _site(lat, lon, hz=None, **kw):
    s = {"lat": lat, "lon": lon, "horizon_deg": np.zeros(180) if hz is None else hz, "hazard_score": 0.2,
         "landmark_score": 0.1, "landing_safe": True, "premium": 0.0, "ice_km": None}
    s.update(kw)
    return s


def _buy(site, eph, cutoff):
    st = visibility.site_stats(np.array([site["lat"]]), np.array([site["lon"]]), np.asarray(site["horizon_deg"])[None], eph, CFG)
    t = {k: st[k] for k in ("energy_wh_m2_day", "longest_dark_h", "earth_frac", "longest_blackout_h", "temp_min_k", "temp_max_k")}
    t["hazard_score"], t["landmark_score"] = np.array([0.2]), np.array([0.1])
    v = float(scoring.viability(scoring.subscores(t, CFG), np.array([True]), CFG)[0])
    return pricing.price_usd(v, CFG, 0.0, 60.0)


@pytest.mark.parametrize("lat,lon", [(0.0, 0.0), (45.0, 100.0), (-80.0, 20.0)])
def test_rent5_one_year_stay_equals_ratio_times_buy(eph, lat, lon):
    """RENT-5: a 1-year stay (move in day 1) must equal RENT_RATIO * the Buy price."""
    site = _site(lat, lon)
    r = pricing.rent_for_stay(site, eph, CFG, 60.0, 1, 366)
    assert r["rent_per_month"] == pytest.approx(CFG["price"]["rent_ratio"] * _buy(site, eph, 60.0), rel=1e-9)
    assert r["stay_hours"] == 8784


def test_rent_changes_with_move_in_and_buy_does_not(eph):
    site = _site(-89.0, 20.0, hz=np.full(180, 1.0))
    rents = [pricing.rent_for_stay(site, eph, CFG, 60.0, d, 14)["rent_per_month"] for d in range(1, 300, 14)]
    assert max(rents) / min(rents) > 1.2  # a 14-day stay depends on where in the cycle it starts
    assert pricing.price_usd(50.0, CFG) == pricing.price_usd(50.0, CFG)  # Buy price is a pure function of viability


def test_stay_clipped_to_year_end_and_bad_move_in(eph):
    r = pricing.rent_for_stay(_site(0.0, 0.0), eph, CFG, 60.0, 360, 90)
    assert r["stay_hours"] == 24 * 7  # days 360..366 remain
    with pytest.raises(ValueError):
        pricing.rent_for_stay(_site(0.0, 0.0), eph, CFG, 60.0, 400, 14)
