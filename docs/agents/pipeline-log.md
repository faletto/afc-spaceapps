# Pipeline Claude — log

*Single writer: **Pipeline Claude**. Others read only. Keep `## Resume here
- Branch: `pipeline` · Contract: **v2** (+H4 notes) · P0–P4 ✅ (H0, H3, H4 merged to main)
- Real data for both tiers in app/public/data (~106 MB raw). Rebuild: `make polar` (cells ~12 min, cached in data/work/polar_cells.npz; plots ~30 s) then `python -m lunar_listings data` (~30 s; needs data/work/{dem_global_32.npy,terrain_global.npz,terrain_polar_*_20m.npz}, regenerate via terrain.resample_global / build_global_stats / build_polar_stats).
- Next: P5 — blurbs (config/blurbs.yaml, 20–30 templates, hash of plot ID), featured plots, rent reference (`pricing.py` rent for a stay: recompute stats over [move_in, move_in+stay] at the best cell) + **rent golden vectors**, TEMP-4 Diviner note, find the demo before/after number. Then P6 (payload/perf, README pipeline section). Read spec §3.10 + req §5.6.
- Open: Q-P6 (flat power score; spec penalty kept), HOR-2 external profile (needs a human-supplied Moon Trek/QuickMap profile), TEMP-4 Diviner (download needed later).
- Env: `.venv` py3.11; `make test` = 61 tests; NEVER `make stub` over real data (guarded).

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| P0 | ✅ | 86cc05e | H0 | stub + contract v1 |
| P1 | ✅ | see git log | — | ephemeris, geometry, global+polar terrain (20 m) |
| P2 | ✅ | see git log | H3 | validate PASS 0.006°, sanity suite |
| P3 | ✅ | see git log | H3/H4 | gates calibrated + approved |
| P4 | ✅ | see git log | H4 | horizons (cone test ≤0.05°), polar tier real, reviewer pass |
| P5 | ⬜ | | | |
| P6 | ⬜ | | | |

## Contract/handoffs
- H4 · 14 Nov · contract v2 + H4 notes (CONTRACT.md) · real polar tier: 78,464 plots, horizon tiles for every plot (uint8·0.16−6°), projection descriptor, gates (habitat 168 h, ice 2 km), shared scarcity cutoff, new global prices. ≈106 MB raw in app/public/data. Known: polar `s_power` small under spec penalty (Q-P6).
- H3 · 14 Nov · contract **v2** · real Moon-wide data (global tier), ≈72 MB app/public/data (polar still stub). `make data` regenerates global; `make stub` now refuses to overwrite real data without `--force`. Golden vectors v1 committed. Known: Q-P6 power score flat Moon-wide; Q-P7 below.
- H0 · 14 Nov · contract v1 · stub data (fake values, real formats), ≈41 MB, 738 files. Details in CONTRACT.md 'v1 concrete details'. Known: polar ≈78k plots (disk to 85°S), not 91k; polar projection is a stand-in.
<!-- newest first: H#, date/time, contract vN, main@sha, what's new, files, size MB, known issues -->

## Open questions
- Q-P6 · 14 Nov · Moon-wide `s_power` is ≈ 0.04 on almost every plot: longest night ≈ 360 h → penalty(360; h50=120, k=2) = 0.10, times norm(energy) ≈ 0.45. Power therefore doesn't discriminate Moon-wide (only polar light matters). Viability tops out ≈ 65, scarcity cutoff ≈ 58, top Moon-wide price ≈ $730K. Spec values used as-is; proposal for the P3 calibration: raise `penalty.dark.h50` to ~400 h (or apply the dark penalty only in the polar tier). ASSUMED keep spec until a human decides.
- (answered, see below) Q-P5 · 14 Nov · Reviewer: Moon-wide plots use `terrain_margin` (m≡0) so Earth contact needs only ≥ 1° elevation, vs COMM-1's 5° cutoff. Follows the spec's decided mode. My default: ASSUMED keep. Please confirm for the Moon-wide tier (or set `comms.mode: absolute` there).
- Q-P2 · 14 Nov · Spec's TSI sanity band 1320–1412 W/m² is too tight: 2028 gives 1310–1413 (L☉/4πr² is correct). ASSUMED band 1300–1420; tell me if you want the spec fixed.
- Q-P1 · 14 Nov · Stub data (41 MB) committed to git; real data likely larger (detail JSON). Default: ASSUMED commit if < 50 MB total, else Release asset (per answers.md).
<!-- Q-P#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
- Q-P7: data folder 72 MB > 50 MB budget — commit anyway or Release asset? · answer: commit anyway (chat, 14 Nov); commit real data only at handoffs (H3, H4, H6).
- Q-P5: Moon-wide Earth contact uses terrain_margin (1° over zero terrain) · answer: 'use your best judgement' (chat) → KEEP terrain_margin · 14 Nov.
- Q-P4: PGDA throttled to ~1 MB/s; skip the 3.8 GB LDSM 20 m slope product and derive slope from the 20 m DEM · answer: yes, approved in chat · 14 Nov. Safe-fraction therefore comes from our own slope (central differences on 20 m DEM), not LDSM.
- Q-P3: set safety roughness/relief normalisation ranges from data (roughness 0–600 m, relief 0–4000 m, Moon-wide tier; at 1° plots median roughness is 276 m / relief 1950 m) · answer: yes, approved in chat · 14 Nov. Spec §4 values (0–50 / 0–2000) are superseded; config updated. Humans may want to update the spec text.
<!-- Q-P#: answer · source (answers.md / chat) · date -->

## Requests to App Claude
- R-P1 · 14 Nov · FYI: root `Makefile` and `.gitignore` were created by Pipeline (not in the ownership table). Ask for edits (e.g. npm targets) via `## Requests to Pipeline Claude` in your log. Also: derive tile indices from `cols.json` bounds/projection, and decode horizons with `offset_deg` (see CONTRACT v1).
<!-- R-P#: what I need from App · why · by when -->

## Replies to App Claude
<!-- reply to R-A#: … -->

## Done log
- 14 Nov · P4 · projection, horizons.py (Numba; 1.25 M cells in 11.5 min), polar build, export, sanity tests, reviewer fixes (polar far-side rule, global median, premiums) · H4
- 14 Nov · P3 (part) · landmarks (1,454), land.py, scoring/pricing wired into plots.build_global (viability/price/rent on real global data); crater rim/floor via plot TPI p90/p10, thresholds ±300 m ASSUMED · see git log
- 14 Nov · P1 complete (20 m polar stats) + P2 validate.py PASS · see git log
- 14 Nov · P1/P2 · polar terrain code, visibility.py + tests (28 pass) · see git log
- 14 Nov · P1 · global terrain (resample 1/32°, slope, plot stats) on real DEM; Q-P3 ranges applied; DEM fetch in progress (20 m DEM + slope remaining) · see git log
- 14 Nov · P1 (part 1) · Horizons fetch+parser, ephemeris_2028.csv (8784 rows, 0.7 MB), ephemeris.py, geometry.py + tests · see git log
- 14 Nov · P0 · scaffold + config + stub, contract v1 · 86cc05e (+ hardening commit) · 10 passed
<!-- newest first: date time · WP · what · sha · tests -->
