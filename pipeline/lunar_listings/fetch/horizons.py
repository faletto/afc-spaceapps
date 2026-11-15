"""JPL Horizons client (spec §3.1). Caches every response; sequential requests only; retries with backoff."""

import hashlib
import time
from pathlib import Path

import requests

URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
CACHE = Path(__file__).resolve().parents[3] / "data" / "cache" / "horizons"


def ephemeris_params(year: int) -> dict:
    return {
        "format": "text",
        "COMMAND": "'301'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'500@399'",
        "START_TIME": f"'{year}-01-01'",
        "STOP_TIME": f"'{year + 1}-01-01'",
        "STEP_SIZE": "'1h'",
        "QUANTITIES": "'14,15,19,20'",
        "ANG_FORMAT": "'DEG'",
        "CSV_FORMAT": "'YES'",
        "RANGE_UNITS": "'KM'",
    }


def get(params: dict, cache_dir: Path = CACHE, retries: int = 4) -> str:
    """Return response text, from cache when present."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(repr(sorted(params.items())).encode()).hexdigest()[:16]
    f = cache_dir / f"{key}.txt"
    if f.exists():
        return f.read_text()
    err = None
    for i in range(retries):
        try:
            r = requests.get(URL, params=params, timeout=120)
            r.raise_for_status()
            if "$$SOE" not in r.text:
                raise RuntimeError("Horizons returned no ephemeris: " + r.text[:300])
            f.write_text(r.text)
            return r.text
        except (requests.RequestException, RuntimeError) as e:
            err = e
            time.sleep(2**i)
    raise RuntimeError(f"Horizons fetch failed: {err}")
