# Pipeline Claude — log

*Single writer: **Pipeline Claude**. Others read only. Keep `## Resume here
- Branch: `pipeline` · Contract: **v1** (stub, H0) · P0 done @ 86cc05e + contract-hardening commit
- Env: `make setup` (uv venv py3.11 at repo-root `.venv`), `make stub`, `make test`; stub ≈ 41 MB in `app/public/data/` (committed once; avoid regenerating/committing churn)
- P1 part 1 done (ephemeris + geometry, tests green). Next: terrain (global resample, slope/roughness/relief; polar crop/240 m cells), spec §3.4 + DEM fetch/sources.yaml; then golden TSI/geometry check vs Horizons.
- Blockers: none. Note: system python is 3.15; always use `.venv` (3.11).

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| P0 | ✅ | 86cc05e | H0 | stub + contract v1 |
| P1 | ⬜ | | | |
| P2 | ⬜ | | | |
| P3 | ⬜ | | | |
| P4 | ⬜ | | | |
| P5 | ⬜ | | | |
| P6 | ⬜ | | | |

## Contract/handoffs
- H0 · 14 Nov · contract v1 · stub data (fake values, real formats), ≈41 MB, 738 files. Details in CONTRACT.md 'v1 concrete details'. Known: polar ≈78k plots (disk to 85°S), not 91k; polar projection is a stand-in.
<!-- newest first: H#, date/time, contract vN, main@sha, what's new, files, size MB, known issues -->

## Open questions
- Q-P2 · 14 Nov · Spec's TSI sanity band 1320–1412 W/m² is ~1 W/m² too tight: 2028 perihelion gives 1413.1 (L☉/4πr² is correct). ASSUMED band 1320–1420; tell me if you want the spec fixed.
- Q-P1 · 14 Nov · Stub data (41 MB) committed to git; real data likely larger (detail JSON). Default: ASSUMED commit if < 50 MB total, else Release asset (per answers.md).
<!-- Q-P#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
<!-- Q-P#: answer · source (answers.md / chat) · date -->

## Requests to App Claude
- R-P1 · 14 Nov · FYI: root `Makefile` and `.gitignore` were created by Pipeline (not in the ownership table). Ask for edits (e.g. npm targets) via `## Requests to Pipeline Claude` in your log. Also: derive tile indices from `cols.json` bounds/projection, and decode horizons with `offset_deg` (see CONTRACT v1).
<!-- R-P#: what I need from App · why · by when -->

## Replies to App Claude
<!-- reply to R-A#: … -->

## Done log
- 14 Nov · P1 (part 1) · Horizons fetch+parser, ephemeris_2028.csv (8784 rows, 0.7 MB), ephemeris.py, geometry.py + tests · see git log
- 14 Nov · P0 · scaffold + config + stub, contract v1 · 86cc05e (+ hardening commit) · 10 passed
<!-- newest first: date time · WP · what · sha · tests -->
