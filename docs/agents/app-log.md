# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` · Built against contract v1 (main @ 35351cd, stub data) · Unpushed: 0 after push
- Done: A0, **A1** (loader, MapView, results list, listing shell, fine print footer + dismissible first-load notice). vitest 10, e2e 6, lint/tsc clean.
- Next: A2 — overlay plumbing + legends + opacity; Web Worker scaffold (filter/sort over typed arrays, move `queryResults` there); glossary tooltips (config/glossary.json).
- Blockers: Q-A1 (CI needs `.github/`).
- Known gaps (A1): results list scroll position resets after Back; nearest-feature/landmarks, "why" line, photos/3D tour, rent not yet (later WPs). Listing "why" needs a pipeline field (R-A2).
- ASSUMED: plot half-size global 0.5°/polar 480 m; price bands = quantiles; pills at fit+3 zoom (cap 1500); list excludes off-market; sorts price↑↓/viability/sunlight; main-thread query for now.
- e2e pill-click uses fixed pixel coords (1200×700, 5×300 wheel) — update if layout changes.
- Commands: `cd app && npm ci`, `npm run dev`, `npm test`, `npm run lint`, `npx playwright test`, `npm run build`

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| A0 | ✅ (CI pending) | see git log | no | CI job blocked, Q-A1 |
| A1 | ✅ | see git log | no | stub data; worker + filters in A2/A3 |
| A2 | ⬜ | | | |
| A3 | ⬜ | | | |
| A4 | ⬜ | | | |
| A5 | ⬜ | | | |
| A6 | ⬜ | | | |
| A7 | ⬜ | | | |

## Contract status
<!-- contract version I'm built against; mismatches seen; adaptations made -->

## Open questions
Q-A1: 14 Nov · A0 requires a CI job for app, but `.github/` isn't in my write scope. Who owns it? ASSUMED: leave until answered; I can supply a workflow YAML on request.
<!-- Q-A#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
<!-- Q-A#: answer · source · date -->

## Requests to Pipeline Claude
R-A2: listing needs a one-line 'why' (DET-2) and nearest named feature (DET-1) per plot — add to detail records `{why, nearest_feature, nearest_km}` by H3 (additive). Until then the listing shows plot number and the stub blurb.
R-A1 (RESOLVED: names are s_safety,s_power,s_comms,s_thermal,s_landmark,s_ice; cols.json keys confirmed from stub): confirm exact names of the six `s_*` score columns (spec §5 says `s_safety … s_ice`); I assumed s_safety,s_power,s_comms,s_thermal,s_terrain,s_ice. Also confirm `cols.json` schema keys (`rows`, `columns[{name,dtype,offset,scale}]`).
<!-- R-A#: what I need (field, format, fix) · why · by when -->

## Replies to Pipeline Claude
<!-- reply to R-P#: … -->

## Done log
- 14 Nov · A1 done · listing shell (header, price+facts, scores, facts, fine print, notice), Back/Escape · e2e 6 passed
- 14 Nov · A1 (part) · results list + sort + hover link + 2-col layout · vitest 10, e2e 4, lint/tsc clean
- 14 Nov · A1 (part) · MapView + markers + selection store · vitest 8, e2e 2, lint/tsc clean
- 14 Nov · A1 (part) · loader + types vs contract v1 · vitest 5 passed, lint/tsc clean
<!-- newest first: date time · WP · what · sha · tests -->
