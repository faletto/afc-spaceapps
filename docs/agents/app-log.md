# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` · Built against contract v1 (main @ 35351cd, stub data) · H3 NOT landed yet (checked 14 Nov: main still H0; Pipeline in P1/P2).
- Done: A0, A1, A2; **A3 prep on stub**: filters (price range w/ k/M parsing, land type multi-select, hide off-market, clear) wired through worker; query now runs in `App` via `useResultsQuery` and lives in the store (`results` = list ids/total + `passing` mask that drives map markers); "N plots match"; **D-6 e2e** (price unchanged across overlay/filters/sort/tier/selection) green; perf: filter+sort ≈ 11 ms (64.8k rows) / 12 ms (78k polar) in Node. vitest 17, e2e 10.
- Next: when H3 lands (`git fetch`; CONTRACT v2?), merge origin/main, rerun e2e on real data, check first-load < 3 s, facts/why line from detail, then run `reviewer` subagent (end of A3) and merge `app` → `main` at M3. Until then: A4 prep is blocked on golden vectors (H3); could start TypeScript `geo/projections.ts` + `science/geometry.ts` from spec §3.3.
- Blockers: H3. Unanswered requests to Pipeline: R-A2 (why/nearest feature), R-A3 (glossary.json).
- Known gaps: OV-7 comm window, OV-3 mean/min/max toggle, Home type + "More" filters (A5), Rent tab (A6); results scroll resets after Back; D-6 test has a TODO to add Rent/time-slider.
- ASSUMED: plot half-size global 0.5°/polar 480 m; price bands = quantiles of UNFILTERED prices; pills at fit+3 zoom (cap 1500); dots scale with zoom, fade under overlay; list excludes off-market always; "Hide off-market" hides grey rings on the map; price filters ignore off-market plots.
- e2e notes: runs against `vite build && preview` (4173); expect timeout 15 s, test timeout 60 s (software GL is slow). Pill-click test uses fixed pixel coords.
- Commands: `cd app && npm ci`, `npm run dev`, `npm test`, `npm run lint`, `npx playwright test`, `npm run build`

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| A0 | ✅ (CI pending) | see git log | no | CI job blocked, Q-A1 |
| A1 | ✅ | see git log | no | stub data; worker + filters in A2/A3 |
| A2 | ✅ (OV-7 comm window deferred) | see git log | no | worker + overlays + tooltips |
| A3 | 🟡 prep done on stub; waiting H3 | see git log | no | filters + D-6 test done |
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
- 14 Nov · A3 prep · filters (price/land/hide-off), query lifted to App+store, map mask, D-6 e2e, perf check · vitest 17, e2e 10
- 14 Nov · A2 · overlays (6 names, legend, opacity), compute worker (filter/sort), glossary tooltips; fixed deck.gl null-image overlay error and dots hiding overlay · vitest 13, e2e 8
- 14 Nov · A1 done · listing shell (header, price+facts, scores, facts, fine print, notice), Back/Escape · e2e 6 passed
- 14 Nov · A1 (part) · results list + sort + hover link + 2-col layout · vitest 10, e2e 4, lint/tsc clean
- 14 Nov · A1 (part) · MapView + markers + selection store · vitest 8, e2e 2, lint/tsc clean
- 14 Nov · A1 (part) · loader + types vs contract v1 · vitest 5 passed, lint/tsc clean
<!-- newest first: date time · WP · what · sha · tests -->
