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
