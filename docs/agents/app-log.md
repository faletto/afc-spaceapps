# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` · Built against contract v1 (main @ 35351cd, stub data) · Unpushed: 0 after push
- Done: A0 scaffold; A1 loader (`src/data/loader.ts`: manifest+version check, cols decode, ephemeris, lazy detail/horizon tiles, Source injection) + tests on stub data.
- In progress: A1 — next MapView (two tiers, deck.gl OrthographicView, basemap bitmap, dot↔pill markers), results list, listing shell.
- Blockers: Q-A1 (CI job needs `.github/`).
- Commands: `cd app && npm ci`, `npm run dev`, `npm test`, `npm run lint`, `npx playwright test`, `npm run build`
- Polar: use cols.json bounds/projection (stub: azimuthal-equidistant stand-in), not formulas.

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
- 14 Nov · A1 (part) · loader + types vs contract v1 · vitest 5 passed, lint/tsc clean
<!-- newest first: date time · WP · what · sha · tests -->
