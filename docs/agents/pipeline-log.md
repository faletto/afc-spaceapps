# Pipeline Claude — log

*Single writer: **Pipeline Claude**. Others read only. Keep `## Resume here
- Branch: `pipeline` · Contract v2 (+H4, H6, P6 notes) · P0–P6 ✅. From-scratch rebuild verified byte-identical (737 files; `make all-data`).
- P6 done: `make terrain/all-data`, `pipeline/README.md`, payload check (gzip core ≈ 9 MB; polar detail+horizon ≈ 11 MB), App requests R-A2/A3/A4/A5 answered (nearest_feature/km, glossary.json, manifest v2, basemap_small).
- Cross-checks DONE (NASA data): `crosscheck.py` → docs/validation.md. LOLA illumination (PGDA): Sun r=0.988, RMSE 0.024; Earth r=0.957 (bias −0.066, expected from the 1° margin); PSR agreement 98.2%. Diviner (PDS): see Q-P8. HOR-2 external profile no longer needed (LOLA illumination serves). NFR-4: no raw-size limit (human), no trim.
- Q-P6 RESOLVED (human): net-energy Sun score (see CONTRACT 'Q-P6 change'); data + goldens regenerated; new demo SP-0032-0154 (day 218 $22,034/mo → day 232 $10,064/mo, −54%). Q-P8 RESOLVED (leave + label modelled). Nothing open except tuning of the ASSUMED load/battery constants if wanted.
- Maintenance: bug fixes requested by App in app-log.md `## Requests to Pipeline Claude`. Rebuild: `make all-data`. NEVER `make stub` over real data.

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| P0 | ✅ | 86cc05e | H0 | stub + contract v1 |
| P1 | ✅ | see git log | — | ephemeris, geometry, global+polar terrain (20 m) |
| P2 | ✅ | see git log | H3 | validate PASS 0.006°, sanity suite |
| P3 | ✅ | see git log | H3/H4 | gates calibrated + approved |
| P4 | ✅ | see git log | H4 | horizons (cone test ≤0.05°), polar tier real, reviewer pass |
| P5 | ✅ | see git log | H6 | blurbs, rent ref + golden, demo number; TEMP-4 deferred |
| P6 | ✅ | see git log | final | README, reproducibility verified, App requests R-A2..A5 |

## Contract/handoffs
- H6 · 14 Nov · contract v2 + H6 notes · detail `blurb`/`why`, `featured` flag, rent reference + `golden_rent_v1.json`. Demo number: SP-0172-0148, 14-day stay: day 274 → $16,758/mo, day 288 → $7,129/mo (−57%, Earth blackout). TEMP-4 (Diviner) not done.
- H4 · 14 Nov · contract v2 + H4 notes (CONTRACT.md) · real polar tier: 78,464 plots, horizon tiles for every plot (uint8·0.16−6°), projection descriptor, gates (habitat 168 h, ice 2 km), shared scarcity cutoff, new global prices. ≈106 MB raw in app/public/data. Known: polar `s_power` small under spec penalty (Q-P6).
- H3 · 14 Nov · contract **v2** · real Moon-wide data (global tier), ≈72 MB app/public/data (polar still stub). `make data` regenerates global; `make stub` now refuses to overwrite real data without `--force`. Golden vectors v1 committed. Known: Q-P6 power score flat Moon-wide; Q-P7 below.
- H0 · 14 Nov · contract v1 · stub data (fake values, real formats), ≈41 MB, 738 files. Details in CONTRACT.md 'v1 concrete details'. Known: polar ≈78k plots (disk to 85°S), not 91k; polar projection is a stand-in.
<!-- newest first: H#, date/time, contract vN, main@sha, what's new, files, size MB, known issues -->

## Open questions
- Q-P8 · 14 Nov · TEMP-4 (Diviner, NASA PDS) shows our T1 matches Diviner for PSRs (40 K vs 43 K median) but overstates lit-site maxima (annual max median 207 K vs binned Diviner ≈ 65–130 K; binned maps average out extremes) and the 95 K night floor (Diviner nights ≈ 65 K median). The thermal sub-score uses swing = max − min, so polar comfort is likely overstated. Proposal (not applied): lower `thermal.floor_k` for polar and add a shadow-fraction term to T_max; or leave and label as modelled. ASSUMED leave until humans decide.
- Q-P6 · 14 Nov · Moon-wide `s_power` is ≈ 0.04 on almost every plot: longest night ≈ 360 h → penalty(360; h50=120, k=2) = 0.10, times norm(energy) ≈ 0.45. Power therefore doesn't discriminate Moon-wide (only polar light matters). Viability tops out ≈ 65, scarcity cutoff ≈ 58, top Moon-wide price ≈ $730K. Spec values used as-is; proposal for the P3 calibration: raise `penalty.dark.h50` to ~400 h (or apply the dark penalty only in the polar tier). ASSUMED keep spec until a human decides.
- (answered, see below) Q-P5 · 14 Nov · Reviewer: Moon-wide plots use `terrain_margin` (m≡0) so Earth contact needs only ≥ 1° elevation, vs COMM-1's 5° cutoff. Follows the spec's decided mode. My default: ASSUMED keep. Please confirm for the Moon-wide tier (or set `comms.mode: absolute` there).
- Q-P2 · 14 Nov · Spec's TSI sanity band 1320–1412 W/m² is too tight: 2028 gives 1310–1413 (L☉/4πr² is correct). ASSUMED band 1300–1420; tell me if you want the spec fixed.
- Q-P1 · 14 Nov · Stub data (41 MB) committed to git; real data likely larger (detail JSON). Default: ASSUMED commit if < 50 MB total, else Release asset (per answers.md).
<!-- Q-P#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
- Hot property question (14 Nov): human chose option 1 → Hot property is computed per tier (P95 within Moon-wide and within polar); scarcity cutoff stays shared. Config comment + CONTRACT note; data regenerated; test added (185).
- Q-P8 (reopened with evidence, human said 'yes' 14 Nov): Diviner polar average max 202 K / min 50 K (Williams 2017) → our lit-site max (207 K) is right, our 95 K night floor is too warm for the poles → `thermal.polar_floor_k: 50` applied to the polar tier and polar rent; Moon-wide stays 95 K. Q-P6 constants cross-checked against NASA numbers (153–160 Wh/kg Li-ion; NIAC AeSI 15-day night ≈ 490 W, 1.8 t battery) and kept.
- Q-P4 follow-up (14 Nov): human asked to get the slope product → LDSM_80S_20MPP_ADJ downloaded (3.78 GB, sha256 pinned) and now used for polar slopes/safe fractions; own-slope vs LDSM agree (plot mean slope r = 1.000, RMSE 0.05°, safe-fraction RMSE 0.006); data, goldens and validation report regenerated. Manifest `sources.polar` records DEM and slope product.
- Q-P8: polar T1 maxima/night floor vs Diviner · answer: human said "do that" → option 1: leave the model, label temperatures as modelled (glossary text updated; app should keep the 'modelled' wording) · 14 Nov.
- Q-P6: Sun/power score → net estimated energy production over the mission duration (full year Buy, stay window Rent); net = harvest − continuous load, with battery-mass factor for the longest night · answer: chosen in chat (human) 14 Nov. Constants load 500 W, ref 3000 W, 150 Wh/kg, 2000 kg are ASSUMED.
- Q-P7: data folder 72 MB > 50 MB budget — commit anyway or Release asset? · answer: commit anyway (chat, 14 Nov); commit real data only at handoffs (H3, H4, H6).
- Q-P5: Moon-wide Earth contact uses terrain_margin (1° over zero terrain) · answer: 'use your best judgement' (chat) → KEEP terrain_margin · 14 Nov.
- Q-P4: PGDA throttled to ~1 MB/s; skip the 3.8 GB LDSM 20 m slope product and derive slope from the 20 m DEM · answer: yes, approved in chat · 14 Nov. Safe-fraction therefore comes from our own slope (central differences on 20 m DEM), not LDSM.
- Q-P3: set safety roughness/relief normalisation ranges from data (roughness 0–600 m, relief 0–4000 m, Moon-wide tier; at 1° plots median roughness is 276 m / relief 1950 m) · answer: yes, approved in chat · 14 Nov. Spec §4 values (0–50 / 0–2000) are superseded; config updated. Humans may want to update the spec text.
<!-- Q-P#: answer · source (answers.md / chat) · date -->

## Requests to App Claude
- R-P1 · 14 Nov · FYI: root `Makefile` and `.gitignore` were created by Pipeline (not in the ownership table). Ask for edits (e.g. npm targets) via `## Requests to Pipeline Claude` in your log. Also: derive tile indices from `cols.json` bounds/projection, and decode horizons with `offset_deg` (see CONTRACT v1).
<!-- R-P#: what I need from App · why · by when -->

## Replies to App Claude
R-A9 (reply, 14 Nov): `golden_rent_v1.json` now embeds the real per-site `premium` (polar sites carry +75% / +25% as shipped; Moon-wide synthetic sites stay 0), so its 1-year rent matches the shipped `rent_avg`. Regenerated; TS parity tests need the new golden (SP-0172-0148 demo number changes accordingly). Premium is not a column; derive it as price / (5000·exp(k·v/100)·scarcity) if needed, or ask and I'll add one.
Q-A3 (reply, 14 Nov): full override. `scoring.viability` uses `home_types.<type>.weights` instead of `config.weights`, keys not listed count 0, normalised by Σw over listed keys. Your assumption is correct.
- R-A6 (RESOLVED, 14 Nov): `ephemeris.bin` is now the real data from `pipeline/data/ephemeris_2028.csv` (the export never replaced the v1 stub file; found and fixed in the full audit). `test_edge_data.py::test_ephemeris_bin_matches_parsed_horizons_csv` guards it. Regenerate your copy by merging `main`.
- R-A7 (RESOLVED, 14 Nov): `horizons.quantize/dequantize` defaults are now unit 0.16, offset −6.0 (they were −3.0); `golden_v1.json` `horizon_quantisation` cases regenerated with offset −6 and include NaN/clamp cases; un-skip your test.
<!-- reply to R-A#: … -->

## Done log
- 14 Nov · Hot property per tier (cli data stage, test_edge_data), data regenerated
- 14 Nov · Q-P8 applied: polar night floor 50 K (config, kernel `floor_k`, polar_build, rent), polar cells rebuilt, data/goldens/validation regenerated, +3 tests (184); new demo number SP-0032-0154 $15,084 → $6,890 (−54%)
- 14 Nov · NASA LDSM slope product adopted (replaces own slope), ruff check + format clean across pipeline/, stage-2 now re-reads terrain stats (no stale cache) · contract unchanged
- 14 Nov · Full audit (human request): found/fixed real ephemeris.bin (was still the v1 stub, R-A6), quantisation default/golden mismatch (R-A7), stale cached landmark scores in polar cells, Artemis III landmark positions now IAU feature centres (Faustini, Haworth, Nobile, de Gerlache, Shackleton, Mons Malapert, Mons Mouton, Cabeus) instead of approximate ones, best_window with stay > window, landmark_score_and_nearby with < max_nearby landmarks, quantize NaN, silent integer wrap-around in column casts (now saturating), shared contract.py (export no longer imports stub). +104 edge-case/integrity tests (179 total). Auditor follow-ups: horizon quantisation constants live once in contract.py; polar disc latitude from config; golden rent cutoff read from the exported config.json (and tested); golden generation fails loudly without polar data; no silent 'stub' tier fallback (now 'missing'); viability raises on zero weights; dead config key removed.
- 14 Nov · Q-P6 · net-energy power score (scoring.power_score), config power.*, goldens regenerated, data regenerated (cutoff 62.3), new demo number
- 14 Nov · P6 · NASA cross-checks: LOLA illumination (HOR-2) + Diviner (TEMP-4) in docs/validation.md; sources.yaml extended
- 14 Nov · P6 · make terrain/all-data, README, rebuild byte-identical, glossary.json, nearest_feature, basemap_small · final handoff
- 14 Nov · P5 · blurbs, featured, rent_for_stay + rent golden, demo number · H6
- 14 Nov · P4 · projection, horizons.py (Numba; 1.25 M cells in 11.5 min), polar build, export, sanity tests, reviewer fixes (polar far-side rule, global median, premiums) · H4
- 14 Nov · P3 (part) · landmarks (1,454), land.py, scoring/pricing wired into plots.build_global (viability/price/rent on real global data); crater rim/floor via plot TPI p90/p10, thresholds ±300 m ASSUMED · see git log
- 14 Nov · P1 complete (20 m polar stats) + P2 validate.py PASS · see git log
- 14 Nov · P1/P2 · polar terrain code, visibility.py + tests (28 pass) · see git log
- 14 Nov · P1 · global terrain (resample 1/32°, slope, plot stats) on real DEM; Q-P3 ranges applied; DEM fetch in progress (20 m DEM + slope remaining) · see git log
- 14 Nov · P1 (part 1) · Horizons fetch+parser, ephemeris_2028.csv (8784 rows, 0.7 MB), ephemeris.py, geometry.py + tests · see git log
- 14 Nov · P0 · scaffold + config + stub, contract v1 · 86cc05e (+ hardening commit) · 10 passed
<!-- newest first: date time · WP · what · sha · tests -->
