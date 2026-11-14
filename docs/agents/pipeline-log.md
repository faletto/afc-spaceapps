# Pipeline Claude — log

*Single writer: **Pipeline Claude**. Others read only. Keep `## Resume here
- Branch: `pipeline` (pushed) · Contract: v1 (stub) · WP: P1 nearly done, P2 started
- Done: ephemeris CSV, geometry, global terrain (real DEM), polar terrain code (validated on 80 m), `visibility.py` (ref + Numba kernel, parity-tested; whole Moon 64,800 sites × 8784 h in ~10 s, flat horizon).
- In progress: 20 m polar DEM download (`curl -C -` resumable; check `ls -l data/raw`; final size 2696082051). When complete: `make fetch` (records sha256; LDSM dropped, Q-P4), then `build_polar_stats('data/raw','data/work',cfg)` auto-uses the 20 m DEM.
- Next: P2 rest — global plots/SAFE export glue, `validate.py` (EPH-3 Horizons site comparison, ≤1°/≤0.1°), sanity suite, docs/validation.md; then P3 (land, scoring, pricing).
- Env: `.venv` py3.11; `make test` (28 tests); intermediates in gitignored `data/work/`.

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
- Q-P2 · 14 Nov · Spec's TSI sanity band 1320–1412 W/m² is too tight: 2028 gives 1310–1413 (L☉/4πr² is correct). ASSUMED band 1300–1420; tell me if you want the spec fixed.
- Q-P1 · 14 Nov · Stub data (41 MB) committed to git; real data likely larger (detail JSON). Default: ASSUMED commit if < 50 MB total, else Release asset (per answers.md).
<!-- Q-P#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
- Q-P4: PGDA throttled to ~1 MB/s; skip the 3.8 GB LDSM 20 m slope product and derive slope from the 20 m DEM · answer: yes, approved in chat · 14 Nov. Safe-fraction therefore comes from our own slope (central differences on 20 m DEM), not LDSM.
- Q-P3: set safety roughness/relief normalisation ranges from data (roughness 0–600 m, relief 0–4000 m, Moon-wide tier; at 1° plots median roughness is 276 m / relief 1950 m) · answer: yes, approved in chat · 14 Nov. Spec §4 values (0–50 / 0–2000) are superseded; config updated. Humans may want to update the spec text.
<!-- Q-P#: answer · source (answers.md / chat) · date -->

## Requests to App Claude
- R-P1 · 14 Nov · FYI: root `Makefile` and `.gitignore` were created by Pipeline (not in the ownership table). Ask for edits (e.g. npm targets) via `## Requests to Pipeline Claude` in your log. Also: derive tile indices from `cols.json` bounds/projection, and decode horizons with `offset_deg` (see CONTRACT v1).
<!-- R-P#: what I need from App · why · by when -->

## Replies to App Claude
<!-- reply to R-A#: … -->

## Done log
- 14 Nov · P1/P2 · polar terrain code, visibility.py + tests (28 pass) · see git log
- 14 Nov · P1 · global terrain (resample 1/32°, slope, plot stats) on real DEM; Q-P3 ranges applied; DEM fetch in progress (20 m DEM + slope remaining) · see git log
- 14 Nov · P1 (part 1) · Horizons fetch+parser, ephemeris_2028.csv (8784 rows, 0.7 MB), ephemeris.py, geometry.py + tests · see git log
- 14 Nov · P0 · scaffold + config + stub, contract v1 · 86cc05e (+ hardening commit) · 10 passed
<!-- newest first: date time · WP · what · sha · tests -->
