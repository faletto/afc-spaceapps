import copy

import pytest

from lunar_listings import config


def test_default_loads():
    c = config.load()
    assert c["analysis"]["year"] == 2028 and c["price"]["base_usd"] == 5000 and c["price"]["k"] == 6.9


@pytest.mark.parametrize("mut", [
    lambda c: c["weights"].pop("ice"),
    lambda c: c["price"].update(base_usd=0),
    lambda c: c["comms"].update(mode="nope"),
    lambda c: c["thermal"].update(cold_range_k=[120, 40]),
    lambda c: c["home_types"]["habitat"].update(ref_stay_days=7),
])
def test_invalid_rejected(mut):
    c = copy.deepcopy(config.load())
    mut(c)
    with pytest.raises(config.ConfigError):
        config.validate(c)
