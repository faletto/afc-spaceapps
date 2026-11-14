# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` · Built against contract v1 (main @ 35351cd, stub data) · Unpushed: 0 after push
- Done: A0; A1 loader; MapView; results list (react-window v2 `List`, 2-col rows, cap 200, view-rect + sort via zustand, hover↔map outline, basemap-crop thumbs, facts line). Two-column layout in App.tsx.
- Next in A1: listing shell + fine print (select → right column shows listing, "← Back to results"), Playwright card→listing→back smoke; then A2.
- Blockers: Q-A1 (CI needs `.github/`).
- ASSUMED: plot half-size global 0.5°/polar 480 m; price bands = quantiles; pills at fit+3 zoom (cap 1500); list excludes off-market plots; sorts: price ↑↓, viability, sunlight. Query runs on main thread for now (worker in A2).
- e2e pill-click uses fixed pixel coords (1200×700 viewport, 5×300 wheel) — update if layout changes.
- Commands: `cd app && npm ci`, `npm run dev`, `npm test`, `npm run lint`, `npx playwright test`, `npm run build`

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| A0 | ✅ (CI pending) | see git log | no | CI job blocked, Q-A1 |
| A1 | ⬜ | | | |
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
R-A1 (RESOLVED: names are s_safety,s_power,s_comms,s_thermal,s_landmark,s_ice; cols.json keys confirmed from stub): confirm exact names of the six `s_*` score columns (spec §5 says `s_safety … s_ice`); I assumed s_safety,s_power,s_comms,s_thermal,s_terrain,s_ice. Also confirm `cols.json` schema keys (`rows`, `columns[{name,dtype,offset,scale}]`).
<!-- R-A#: what I need (field, format, fix) · why · by when -->

## Replies to Pipeline Claude
<!-- reply to R-P#: … -->

## Done log
- 14 Nov · A1 (part) · results list + sort + hover link + 2-col layout · vitest 10, e2e 4, lint/tsc clean
- 14 Nov · A1 (part) · MapView + markers + selection store · vitest 8, e2e 2, lint/tsc clean
- 14 Nov · A1 (part) · loader + types vs contract v1 · vitest 5 passed, lint/tsc clean
<!-- newest first: date time · WP · what · sha · tests -->
