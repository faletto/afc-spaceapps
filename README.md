# Lunar Listings

A Zillow-style listings site for the Moon. **Fictional premise, real science:** every plot's price (the "Moonstimate") is
computed from NASA data: JPL Horizons ephemeris, LOLA and PGDA terrain, LRO Diviner temperatures, and IAU place names.
Built for the NASA Space Apps Challenge 2026 (Lunar Landing Site Navigator).

Two tiers of plots:

| Tier | Plots | Resolution | What is modelled |
|---|---|---|---|
| **Moon-wide** | 64,800 (1° × 1°) | 1/32° terrain | Sun and Earth visibility over 2028, slope and roughness, temperature, landmarks |
| **South Pole District** | 78,464 (960 m, inside 85°S) | 240 m cells, terrain horizons every 2° | Terrain-aware light and Earth contact, permanently shadowed regions, ice distance, a 3D Tour |

## Repository layout

| Path | What it is | Docs |
|---|---|---|
| [`pipeline/`](pipeline/) | Python data pipeline (NumPy/Numba). Turns raw NASA data into static files. | [`pipeline/README.md`](pipeline/README.md) |
| [`app/`](app/) | React + deck.gl web app. Loads the static files; no backend. | [`app/README.md`](app/README.md) |
| [`config/`](config/) | Every tunable (weights, power model, price curve, gates) plus blurb and glossary text. | [`pipeline/README.md`](pipeline/README.md#changing-the-model-later) |
| `app/public/data/` | **Generated** data the app loads (the contract between the two halves). Do not hand-edit. | [`docs/agents/CONTRACT.md`](docs/agents/CONTRACT.md) |
| [`docs/`](docs/) | Requirements, technical spec, validation report, agent logs. | [`docs/README.md`](docs/README.md) |

```
NASA data ─► pipeline (make data) ─► app/public/data/*  ─► app (static site) ─► GitHub Pages
                 │                         ▲
                 └─ config/*.yaml ─────────┘  (config.json is exported so the app mirrors the same formulas)
```

## Quick start

Needs Python 3.11 with [uv](https://docs.astral.sh/uv/) and Node 22.

```
make setup            # Python venv + app dependencies
cd app && npm run dev # http://localhost:5173 (data is already committed)
```

The generated data is committed, so you only need the pipeline (`make fetch` downloads about 15 GB) to change the science.

## Commands (repo root)

| Command | What it does |
|---|---|
| `make setup` | Create the Python venv and install pipeline and app dependencies |
| `make all-data` | Rebuild all data from raw downloads (`fetch terrain polar data`); see the pipeline README |
| `make data` | Re-score, re-price and re-export after a config change (about 30 s) |
| `make validate` | Cross-check against NASA data; writes `docs/validation.md` |
| `make test` | Fast checks: pytest (about 6 s) plus app unit tests |
| `make test-all` | Also runs the slow pytest module that rebuilds the Moon-wide tier (about 30 s) |
| `make app` / `make demo` | Production build of the app / preview it at http://localhost:4173 |

End-to-end browser tests: `cd app && npx playwright install chromium && npx playwright test`.

## Deploying

`.github/workflows/app.yml` lints, type-checks and tests the app on every push or PR touching `app/`, and deploys
`app/dist` to GitHub Pages on pushes to `main`. One-time setup: repo Settings → Pages → Source: "GitHub Actions".
The site is about 160 MB, mostly data.

## Status and scope

- Rent (Buy/Rent toggle, move-in dates, rent estimates) is built but switched off: `RENT_ENABLED` in `app/src/features.ts`.
- Prices, rents and scores are model outputs from stated assumptions, not real valuations. Assumptions are listed in
  `config/lunar-listings.yaml` and explained in the app's About dialog and `docs/validation.md`.

## How the team works

Two Claude Code agents (Pipeline and App) built this in parallel, coordinating through `docs/agents/`
(`PLAN.md`, the two logs, `CONTRACT.md`). Rules for agents are in [`CLAUDE.md`](CLAUDE.md).
