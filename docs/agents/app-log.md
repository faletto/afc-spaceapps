# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` · Built against contract v1 (main @ 35351cd, stub data) · Unpushed: 0 after push
- Done: A0, A1, **A2** (overlay selector + legend from ramp JSON + opacity; compute Web Worker owns filter/sort query; glossary `Term` tooltips on Facts/Scores). vitest 13, e2e 8, lint/tsc clean. CI `.github/workflows/app.yml` green.
- Next: A3 — wait for H3 (real Moon-wide data); meanwhile: filters (price range, land type, hide off-market), facts-line/why line wiring, **e2e "Buy price never changes with UI state"**, perf for 64,800 plots (filter < 200 ms). Read req §5.2–5.4, §9.
- Blockers: none. Check `git fetch` for H3 / contract v2.
- Known gaps: comm-window overlay (OV-7) and temperature mean/min/max toggle (OV-3) not built (P1, need time slider/extra rasters); glossary is an app-side fallback (R-A3); results scroll resets after Back.
- ASSUMED: plot half-size global 0.5°/polar 480 m; price bands = quantiles; pills at fit+3 zoom (cap 1500); dots scale with zoom and fade to 35% under an overlay; list excludes off-market; sorts price↑↓/viability/sunlight.
- e2e pill-click uses fixed pixel coords (1200×700, 5×300 wheel) — update if layout changes. e2e overlay test fails on console errors (deck.gl logs layer errors there).
- Commands: `cd app && npm ci`, `npm run dev`, `npm test`, `npm run lint`, `npx playwright test`, `npm run build`

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| A0 | ✅ (CI pending) | see git log | no | CI job blocked, Q-A1 |
| A1 | ✅ | see git log | no | stub data; worker + filters in A2/A3 |
| A2 | ✅ (OV-7 comm window deferred) | see git log | no | worker + overlays + tooltips |
| A3 | ⬜ | | | |
| A4 | ⬜ | | | |
| A5 | ⬜ | | | |
| A6 | ⬜ | | | |
| A7 | ⬜ | | | |

## Contract status
<!-- contract version I'm built against; mismatches seen; adaptations made -->

## Open questions
<!-- Q-A#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
Q-A1: human granted App Claude permission to write the app CI workflow → `.github/workflows/app.yml` (app/** paths only: lint, tsc, vitest, build, Playwright). Pipeline's job is not in this file. · chat · 14 Nov
<!-- Q-A#: answer · source · date -->

## Requests to Pipeline Claude
R-A3: export `config/glossary.json` (D-1: tooltip text per term with optional `formula`/`source`) and copy it to `app/public/data/glossary.json` (or tell me where). Ids I use: sunlight, longest_night, earth_contact, longest_blackout, temperature, slope, land_type, ice, viability, landing, sun_score, signal, comfort, views, ice_score. Until then I use an app-side fallback (`src/ui/glossary.ts`).
R-A2: listing needs a one-line 'why' (DET-2) and nearest named feature (DET-1) per plot — add to detail records `{why, nearest_feature, nearest_km}` by H3 (additive). Until then the listing shows plot number and the stub blurb.
R-A1 (RESOLVED: names are s_safety,s_power,s_comms,s_thermal,s_landmark,s_ice; cols.json keys confirmed from stub): confirm exact names of the six `s_*` score columns (spec §5 says `s_safety … s_ice`); I assumed s_safety,s_power,s_comms,s_thermal,s_terrain,s_ice. Also confirm `cols.json` schema keys (`rows`, `columns[{name,dtype,offset,scale}]`).
<!-- R-A#: what I need (field, format, fix) · why · by when -->

## Replies to Pipeline Claude
<!-- reply to R-P#: … -->

## Done log
- 14 Nov · A2 · overlays (6 names, legend, opacity), compute worker (filter/sort), glossary tooltips; fixed deck.gl null-image overlay error and dots hiding overlay · vitest 13, e2e 8
- 14 Nov · A1 done · listing shell (header, price+facts, scores, facts, fine print, notice), Back/Escape · e2e 6 passed
- 14 Nov · A1 (part) · results list + sort + hover link + 2-col layout · vitest 10, e2e 4, lint/tsc clean
- 14 Nov · A1 (part) · MapView + markers + selection store · vitest 8, e2e 2, lint/tsc clean
- 14 Nov · A1 (part) · loader + types vs contract v1 · vitest 5 passed, lint/tsc clean
<!-- newest first: date time · WP · what · sha · tests -->
