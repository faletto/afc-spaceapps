import numpy as np
import pytest

from lunar_listings import config, pricing, scoring

CFG = config.load()


def test_penalty_shape():
    assert scoring.penalty(0, 120, 2) == 1
    assert scoring.penalty(120, 120, 2) == 0.5
    assert scoring.penalty(1200, 120, 2) < 0.02


def _table(**kw):
    t = dict(hazard_score=0.0, energy_wh_m2_day=30000, longest_dark_h=0, earth_frac=1.0,
             longest_blackout_h=0, temp_min_k=120, temp_max_k=220, landmark_score=1.0)
    t.update(kw)
    return {k: np.array([v], float) for k, v in t.items()}


def test_perfect_plot_scores_100_and_cap():
    s = scoring.subscores(_table(), CFG)
    v = scoring.viability({k: s[k] for k in s if k != "ice"}, np.array([True]), CFG)
    assert v[0] == pytest.approx(100)
    capped = scoring.viability({k: s[k] for k in s if k != "ice"}, np.array([False]), CFG)
    assert capped[0] == 10


def test_price_anchor_points():
    p = pricing.price_usd(np.array([0, 50, 100]), CFG)
    assert p[0] == 5000 and p[1] == pytest.approx(5000 * np.exp(3.45), rel=1e-9)
    assert 1.5e5 < p[1] < 1.7e5 and 4.9e6 < p[2] < 5.1e6  # ~$160K, ~$5M
    assert pricing.price_usd(90, CFG, cutoff=85) == pytest.approx(1.3 * pricing.price_usd(90, CFG))


def test_range_rent_format_badges():
    lo, hi = pricing.price_range(1000.0, CFG, polar=True)
    assert (lo, hi) == (900.0, 1100.0)
    assert pricing.rent_per_month(100_000.0, CFG) == 600.0
    assert pricing.format_usd(4_200_000) == "$4.2M" and pricing.format_usd(340_000) == "$340K" and pricing.format_usd(5000) == "$5K" and pricing.format_usd(1_234_000) == "$1.23M"
    assert pricing.badges({"price_cut": 1, "hot_property": 1, "earth_view": 1}) == ["hot_property", "earth_view"]


def test_scarcity_cutoff_quantile():
    v = np.arange(100.0)
    assert pricing.scarcity_cutoff(v, CFG) == pytest.approx(97.02, abs=0.01)


def test_landmark_premium():
    import numpy as np
    prem = pricing.landmark_premium(np.array([10.0, 60.0, 10.0]), np.array([False, False, True]), CFG)
    assert list(prem) == [0.25, 0.0, 0.25 + 0.5]


def test_power_score_net_energy():
    # no sun -> 0; abundant sun and no night -> 1; long night costs battery mass
    assert scoring.power_score(0.0, 0.0, CFG) == 0
    assert scoring.power_score(30000.0, 0.0, CFG) == pytest.approx(1.0)
    short, long_ = scoring.power_score(30000.0, 100.0, CFG), scoring.power_score(30000.0, 600.0, CFG)
    assert long_ < short < 1.0
    # harvest below the continuous load -> nothing net (500 W load: 500/(10*0.3)*24 = 4000 Wh/m2/day break-even)
    assert scoring.power_score(3999.0, 0.0, CFG) == 0 and scoring.power_score(5000.0, 0.0, CFG) > 0
