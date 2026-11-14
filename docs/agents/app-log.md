# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` (A4 work on `app-a4` worktree, pushed to `app`) · contract **v2**, main @ 8bc695e merged.
- Done (A4, mostly): `geo/geometry.ts`, `geo/projections.ts` (polar inverse), `science/visibility.ts` (series, stats, runs, best_window, countdown helpers) with **exact golden parity** (`science/visibility.test.ts`: angles 1e-6, stats 1e-9, runs/windows exact); **3D Tour** (`tour/*`, listing `Gallery` Photos | 3D Tour tab, polar only; canvas panorama, Sun/Earth 30-day paths, hollow = behind terrain, countdowns, own time slider until A6). e2e `tour.spec.ts`.
- BLOCKERS for correct tour visuals (Pipeline): **R-A6** shipped `app/public/data/ephemeris.bin` is still the v1 STUB (fake Sun/Earth); parity test builds the real one from `pipeline/data/ephemeris_2028.csv`. **R-A7** golden `horizon_quantisation.cases` were generated with `quantize` default offset −3, manifest/data use −6 → that test is `it.skip`.
- Reviewer pass on A4 done (no blocking; fixed: tour waits for detail.best_cell_xy, primitive effect deps, hollow dots use series flags, wrap-around tests). DEFERRED: TIME-2 — Tour uses its own time slider; A6 must wire it to the global slider (owner: App, A6). Not done: memoising the series per plot, axis clip above 15°.
- Next: South Pole tier polish (not started); countdown golden (none exists; countdown is derived from masks that ARE golden-tested); then merge app→main at M4; A5 (home type, More filters, badges, real ids on cards).
- Commands: `cd app && npm ci`, `npm test`, `npm run lint`, `npx tsc -b`, `npx playwright test`, `npm run build`
- Earlier notes (A3) still apply: ASSUMED plot half-size, price bands, e2e geometry; known gaps OV-7, OV-3, Home type/More filters (A5), Rent (A6).

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| A0 | ✅ (CI pending) | see git log | no | CI job blocked, Q-A1 |
| A1 | ✅ | see git log | no | stub data; worker + filters in A2/A3 |
| A2 | ✅ (OV-7 comm window deferred) | see git log | no | worker + overlays + tooltips |
| A3 | ✅ | see Done log | M3 | real data, filters, D-6 e2e, reviewer pass |
| A4 | 🟡 parity ✅, tour ✅, polar polish + review pending | see git log | no | blocked on R-A6 for real Sun/Earth |
| A5 | ⬜ | | | |
| A6 | ⬜ | | | |
| A7 | ⬜ | | | |

## Contract status
<!-- contract version I'm built against; mismatches seen; adaptations made -->

## Open questions
Q-A2 (mostly resolved by P6 small basemaps; leaving for humans to close): 14 Nov · First-load budget (3 s). NOW: first paint needs cols 4.1 MB + small basemap 0.65 MB + JS ≈ 6 MB; the 8.2 MB full basemap loads in the background. Original text: Startup downloads ≈ 13 MB (basemap 9 MB + cols 4 MB); list is interactive in ~0.3 s on a GPU locally but 9 MB over a slow link may exceed 3 s. ASSUMED: acceptable for the demo (static host, brotli doesn't help JPEG); asked Pipeline for a smaller basemap (R-A5). Humans: is a ~13 MB first load OK, or should I lazy-load the basemap further / require a smaller JPEG?
<!-- Q-A#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
Q-A1: human granted App Claude permission to write the app CI workflow → `.github/workflows/app.yml` (app/** paths only: lint, tsc, vitest, build, Playwright). Pipeline's job is not in this file. · chat · 14 Nov
<!-- Q-A#: answer · source · date -->

## Requests to Pipeline Claude
R-A6 (14 Nov, blocks real 3D Tour): `app/public/data/ephemeris.bin` is still the v1 stub from `stub.py _ephemeris` (sun at t=0 = (0.9996,0,0.0269)). Please write the real one (float32 LE: sun_xyz[8784×3], earth_xyz[8784×3], earth_dist_m[8784], tsi[8784] from `ephemeris.load()`) in the real export and update manifest sha.
R-A7 (14 Nov): `golden.py` `horizon_quantisation.cases` call `horizons.quantize(m)` with its default offset −3.0, but the file declares offset_deg −6 (and data uses −6). Pass `0.16, -6.0` so the cases match; I have the test skipped until then.
R-A4 (14 Nov, after H3): `app/public/data/manifest.json` still says `contract_version: 1` + `stub: true` (tiers: global real, polar stub) while CONTRACT.md says v2. Please bump the manifest field with the data (I built against v2; loader warns on mismatch; my loader test only asserts ≥ 1 until fixed).
R-A5 (14 Nov): first-load weight. `global/basemap.jpg` is now 9.0 MB (hillshade 8192×4096) + 4.1 MB cols.bin ≈ 13 MB at startup. Please consider (a) a smaller JPEG quality/size for the main basemap and/or (b) a `basemap_small.jpg` (~2048×1024) I can show first and for card thumbnails. Not blocking: with a real GPU the list is interactive in ~0.3 s locally; the basemap loads after the list.
R-A3: export `config/glossary.json` (D-1: tooltip text per term with optional `formula`/`source`) and copy it to `app/public/data/glossary.json` (or tell me where). Ids I use: sunlight, longest_night, earth_contact, longest_blackout, temperature, slope, land_type, ice, viability, landing, sun_score, signal, comfort, views, ice_score. Until then I use an app-side fallback (`src/ui/glossary.ts`).
R-A2 (RESOLVED at H6): listing needs a one-line 'why' (DET-2) and nearest named feature (DET-1) per plot — add to detail records `{why, nearest_feature, nearest_km}` by H3 (additive). Until then the listing shows plot number and the stub blurb.
R-A1 (RESOLVED: names are s_safety,s_power,s_comms,s_thermal,s_landmark,s_ice; cols.json keys confirmed from stub): confirm exact names of the six `s_*` score columns (spec §5 says `s_safety … s_ice`); I assumed s_safety,s_power,s_comms,s_thermal,s_terrain,s_ice. Also confirm `cols.json` schema keys (`rows`, `columns[{name,dtype,offset,scale}]`).
<!-- R-A#: what I need (field, format, fix) · why · by when -->

## Replies to Pipeline Claude
<!-- reply to R-P#: … -->

## Done log
- 14 Nov · A4 · science mirror + golden parity (exact), 3D Tour (canvas, paths, countdown, tab), loadConfig · vitest 30, e2e tour 1
- 14 Nov · A3 follow-up 2 · adopted P6: glossary.json via store (fallback), small-basemap-first + thumbnails from small, full basemap background, listing nearest feature · vitest 17, e2e 13
- 14 Nov · A3 follow-up · merged H4+H6 (real polar tier, why/blurb); listing shows why + blurb; loader test pins contract v2 · vitest 17, e2e 12 ×2
- 14 Nov · A3 done · merged H3 (contract v2); real detail fields (id, nearby, P90 slope, buildable area, energy, landing safe); shared basemap blob (1 download), map mounts after first results; Sun/Signal Score sorts; reviewer fixes: "Showing 200 of N", MAP-5 "Off market: not safe to land" hover label, price filter hides off-market plots, band-edge memo, store selectors, detail-tile retry on non-404, worker onerror rejects pending, formatPrice rollover, Escape ignored in inputs, memoised deck data + picking radius + click-selects-hover, D-6 test now filters to ~top-price plots · vitest 17, e2e 12
- 14 Nov · A3 prep · filters (price/land/hide-off), query lifted to App+store, map mask, D-6 e2e, perf check · vitest 17, e2e 10
- 14 Nov · A2 · overlays (6 names, legend, opacity), compute worker (filter/sort), glossary tooltips; fixed deck.gl null-image overlay error and dots hiding overlay · vitest 13, e2e 8
- 14 Nov · A1 done · listing shell (header, price+facts, scores, facts, fine print, notice), Back/Escape · e2e 6 passed
- 14 Nov · A1 (part) · results list + sort + hover link + 2-col layout · vitest 10, e2e 4, lint/tsc clean
- 14 Nov · A1 (part) · MapView + markers + selection store · vitest 8, e2e 2, lint/tsc clean
- 14 Nov · A1 (part) · loader + types vs contract v1 · vitest 5 passed, lint/tsc clean
<!-- newest first: date time · WP · what · sha · tests -->
