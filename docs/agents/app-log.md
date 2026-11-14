# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` · Built against contract v1 (main @ 35351cd, stub data) · Unpushed: 0 after push
- Done: A0; A1 loader; A1 MapView (both tiers, basemap, price-band dots, grey hollow-ring off-market, pills at fit+3 zoom, hover/select outline, tier toggle). e2e: load both tiers; zoom→pill→click selects.
- Next in A1: results list (react-window, cap 200, hover↔card link MAP-3), listing shell + fine print (click pin/card → listing → back), then the Playwright "click card→listing→back" smoke.
- Blockers: Q-A1 (CI needs `.github/`).
- ASSUMED: plot half-size global 0.5°, polar 480 m (`map/tiers.ts`); price bands = quantiles of on-market prices; pills when zoom ≥ fit+3, capped 1500 in view.
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
- 14 Nov · A1 (part) · MapView + markers + selection store · vitest 8, e2e 2, lint/tsc clean
- 14 Nov · A1 (part) · loader + types vs contract v1 · vitest 5 passed, lint/tsc clean
<!-- newest first: date time · WP · what · sha · tests -->
