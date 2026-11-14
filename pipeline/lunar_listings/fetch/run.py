"""`make fetch` ephemeris step: Horizons -> parsed committed CSV."""
from .. import config, ephemeris
from . import horizons


def fetch_ephemeris() -> int:
    year = config.load()["analysis"]["year"]
    n = (366 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 365) * 24
    rows = ephemeris.parse_horizons(horizons.get(horizons.ephemeris_params(year)), n_steps=n)
    ephemeris.write_csv(rows)
    return len(rows)
