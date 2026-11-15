import json

import pytest

from lunar_listings import golden


def test_golden_file_is_current():
    cur = json.loads((golden.OUT / "golden_v1.json").read_text())
    new = json.loads(json.dumps(golden.build()))
    assert cur["version"] == new["version"]
    for a, b in zip(cur["geometry"], new["geometry"], strict=True):
        for k in ("sun_el", "sun_az", "earth_el", "earth_az"):
            assert a[k] == pytest.approx(b[k], abs=1e-6)
    for a, b in zip(cur["visibility"], new["visibility"], strict=True):
        assert a["dark_runs"] == b["dark_runs"] and a["best_window_lander"] == b["best_window_lander"]
        assert a["energy_wh_m2_day"] == pytest.approx(b["energy_wh_m2_day"], rel=1e-9)
    assert cur["pricing"] == new["pricing"] and cur["scoring"] == new["scoring"]


def test_rent_golden_file_reproduces_from_embedded_inputs():
    import numpy as np

    from lunar_listings import config, ephemeris, pricing

    g = json.loads((golden.OUT / "golden_rent_v1.json").read_text())
    cfg, eph = config.load(), ephemeris.load()
    sites = {s["id"]: dict(s, horizon_deg=np.array(s["horizon_deg"])) for s in g["sites"]}
    assert len(g["cases"]) >= 60 and "SP-0032-0154" in sites
    for c in g["cases"][::3]:
        r = pricing.rent_for_stay(
            sites[c["site"]], eph, cfg, g["scarcity_cutoff"], c["move_in_day"], c["stay_days"]
        )
        assert r["rent_per_month"] == pytest.approx(c["rent_per_month"], rel=1e-9)
    demo = {
        c["move_in_day"]: c["rent_per_month"]
        for c in g["cases"]
        if c["site"] == "SP-0032-0154" and c["stay_days"] == 14
    }
    assert demo[218] > 2 * demo[232]  # the demo story: moving in two weeks later cuts the rent a lot


def test_rent_golden_cutoff_matches_exported_config_and_covers_year_end():
    import json

    g = json.loads((golden.OUT / "golden_rent_v1.json").read_text())
    cj = json.loads((golden.OUT.parents[2] / "app" / "public" / "data" / "config.json").read_text())
    assert g["scarcity_cutoff"] == pytest.approx(cj["computed"]["scarcity_viability_cutoff"], abs=1e-3)
    assert any(c["move_in_day"] == 366 for c in g["cases"]) and any(
        c["stay_days"] == 366 and c["move_in_day"] == 1 for c in g["cases"]
    )
    with pytest.raises(FileNotFoundError):
        golden.build_rent(work_dir="/nonexistent")
