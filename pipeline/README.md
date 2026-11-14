# Lunar Listings: data pipeline

Python 3.11 pipeline that turns NASA/JPL data (Horizons ephemeris, LOLA DEMs, IAU nomenclature) into the static
files the app loads from `app/public/data/` (the contract: `docs/technical-spec.md` §5 and
`docs/agents/CONTRACT.md`). Everything is deterministic; raw downloads and intermediates are git-ignored.

## One-time setup
```
make setup          # uv venv (py3.11) + pip install -e pipeline[dev]
```

## Commands (repo root)
| Command | What it does | Time |
|---|---|---|
| `make fetch` | Horizons 2028 ephemeris → `pipeline/data/ephemeris_2028.csv` (cached, committed); LOLA/PGDA DEMs (≈ 11.5 GB, resumable, SHA-256 in `pipeline/data/sources.yaml`) → `data/raw/`; IAU gazetteer → `pipeline/data/landmarks.csv` | ~20–60 min (network) |
| `make terrain` | Global DEM → 1/32° grid, slopes, per-plot stats; polar 20 m DEM → 240 m cell and 960 m plot stats → `data/work/` | ~1 min |
| `make polar` | South Pole tier: terrain horizons for every 240 m cell (Numba), visibility/energy/temperature per cell, best cell per plot, PSR + ice distance → `data/work/polar_plots.npz` | ~12 min (cached in `polar_cells.npz`) |
| `make data` | Moon-wide tier + scoring, pricing, blurbs, overlays, basemaps, tiles, manifest → `app/public/data/` | ~30 s |
| `make all-data` | `fetch terrain polar data` | – |
| `make validate` | EPH-3: our Sun/Earth elevations vs direct Horizons queries → `docs/validation.md`, `docs/img/validation.png` | ~1 min (cached) |
| `make test` | pytest (≈ 70 tests: unit, golden vectors, real-output sanity) | ~25 s |
| `make stub` | Fake data in the real formats (for the app before real data). **Refuses to overwrite real data** without `--force` | seconds |

## Data flow
```
Horizons ──► ephemeris.py ─────────────────────────────┐
LOLA 118 m ► terrain.py (1/32°, slope, stats) ──┐      │
                                                ├► plots.py ─► scoring.py / pricing.py / land.py ─► export.py ─► app/public/data/global
LOLA 20/80 m ► horizons.py (Numba) ► visibility.py (Numba) ► polar_build.py ─────────────────────────► export.py ─► app/public/data/polar
IAU nomenclature ► fetch/gazetteer.py ► land.py (landmark score, nearby)
```
Module map: `polar.py` (stereographic projection + azimuth convention), `geometry.py` (ENU frames, az/el, parallax),
`visibility.py` (sun/Earth visibility, run lists, best windows, thermal), `horizons.py` (terrain skyline),
`scoring.py`, `pricing.py` (incl. `rent_for_stay`, the Python reference for `rent.ts`), `blurbs.py`
(templates in `config/blurbs.yaml`), `golden.py` (vectors the TypeScript mirror must match), `validate.py`.
All tunables are in `config/lunar-listings.yaml` (validated by `config.py`; exported as `config.json`).

## Reproducibility
`make all-data` rebuilds every output from the raw downloads; outputs are byte-identical across runs except
`manifest.json` (timestamp, git SHA). The Horizons responses are cached in `data/cache/horizons/` and the parsed
CSV is committed, so only the DEM and gazetteer downloads need the network.

## Payload (gzip, as a static host serves it)
Core (cols, overlays, ephemeris, config, landmarks) ≈ 9 MB; polar detail + horizon tiles ≈ 11 MB lazy; global
detail ≈ 3 MB lazy; basemaps ≈ 12 MB. Raw on disk ≈ 130 MB (most of it JSON detail tiles).

## Science notes and approved deviations (see `docs/agents/pipeline-log.md` for IDs)
- Earth contact = Earth ≥ 1° above local terrain (`terrain_margin`); Moon-wide plots use zero terrain (Q-P5).
- Roughness/relief normalisation ranges widened for 1° plots (Q-P3); slope computed from the 20 m DEM, not LDSM (Q-P4).
- Horizon tiles: `elevation = v × 0.16° − 6°` (spec −3°; real skylines reach −5.8°).
- Dark/blackout penalty uses the spec's `h50 = 120 h`; this makes the power sub-score small almost everywhere (Q-P6, open).
- Home-type gates calibrated and human-approved on the polar tier (habitat 168 h, ice 2 km).
- Not done: TEMP-4 (Diviner cross-check; needs the south-polar GDR from PDS) and HOR-2's external profile (needs a
  Moon Trek/QuickMap profile). The cone/wall/20 m-vs-80 m checks are in `tests/test_horizons.py`.

## Troubleshooting
- `ModuleNotFoundError` / wrong Python: use `.venv` (system Python may be too new for Numba/rasterio).
- Downloads stall (PGDA throttles): `make fetch` resumes (`curl -C -`).
- Never print arrays; use the summary snippets in the log. Intermediates live in `data/work/` (git-ignored).
