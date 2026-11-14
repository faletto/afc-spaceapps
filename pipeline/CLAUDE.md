# pipeline/CLAUDE.md — Pipeline Claude

You are **Pipeline Claude**. Follow the root `CLAUDE.md` rituals (session start/end, ask questions, logging). Your log: `docs/agents/pipeline-log.md`. Your work packages: `docs/agents/PLAN.md` → P0…P6.

## Scope
- **Write:** `pipeline/**`, `config/**`, `app/public/data/**` (generated only; via `make stub` / `make data`), `docs/agents/pipeline-log.md`, `docs/agents/CONTRACT.md`, `docs/validation.md`, `docs/img/validation.png`.
- **Never write:** `app/**` source, the other log, `answers.md`, the specs.

## Where things are (read only what the package lists)
| Topic | Spec section |
|---|---|
| Repo layout, stack | `docs/technical-spec.md` §1–2 |
| Fetch, ephemeris, geometry | §3.1–3.3 |
| Grids, terrain | §3.4 |
| Horizons | §3.5 |
| Visibility, stats, temperature | §3.6–3.7 |
| Land, ice, scoring, pricing | §3.8–3.10 |
| Export, validation | §3.11–3.12 |
| Config | §4 |
| File formats (the contract) | §5 |
| Acceptance checks | `docs/requirements.md` §9 |

## Commands
`make setup` · `make stub` · `make fetch` · `make data` · `make validate` · `make test` (pytest `-q --maxfail=1`)

## Rules specific to the pipeline
- Data in `data/` is gitignored. Never commit raw DEMs. Commit the parsed ephemeris CSV and any generated output in `app/public/data/` under the budget (ask if it goes over 50 MB).
- **Never print arrays or large tables to the console.** Write a short summary (shape, min/max, a few quantiles) instead.
- **Numba hot loops:** write the pure-Python reference first, test it on a tiny case, then JIT. Keep the reference for the golden vectors.
- **Horizons:** cache every response; no parallel requests; parse the longitude-sign line and assert it.
- **Ask the humans before:**
  - choosing Home-type gate values (P3 calibration: show them the counts table);
  - exceeding size or compute budgets;
  - switching to the simplified-lighting fallback;
  - any contract change after v1.
- **Subagents:**
  - In P1, run the global/polar terrain work in a subagent (worktree isolation) while you do ephemeris + geometry.
  - Use `test-runner` for the full suite and `reviewer` at the end of P2, P3 and P4.
