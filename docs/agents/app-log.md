# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` · Built against contract: v0 (no stub data yet) · Unpushed commits: 0 after push
- Done: A0 scaffold (Vite/React18/TS strict/deck.gl/zustand/react-window/recharts/Vitest/Playwright/ESLint); `data/types.ts`; build, lint, vitest, e2e smoke green.
- Next: A1 once H0 stub data lands on main (`git merge origin/main`): loader, MapView, markers, results list, listing shell.
- Blockers: no stub data yet; CI job for app needs `.github/` (not owned by me, see Open questions Q-A1).
- Commands: `cd app && npm ci`, `npm run dev`, `npm test`, `npm run lint`, `npx playwright test`, `npm run build`
- Note: `s_*` column names in types.ts are ASSUMED (spec elides them).

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
R-A1: confirm exact names of the six `s_*` score columns (spec §5 says `s_safety … s_ice`); I assumed s_safety,s_power,s_comms,s_thermal,s_terrain,s_ice. Also confirm `cols.json` schema keys (`rows`, `columns[{name,dtype,offset,scale}]`).
<!-- R-A#: what I need (field, format, fix) · why · by when -->

## Replies to Pipeline Claude
<!-- reply to R-P#: … -->

## Done log
<!-- newest first: date time · WP · what · sha · tests -->
