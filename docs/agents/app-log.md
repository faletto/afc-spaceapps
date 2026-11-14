# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` · Built against contract **v2** (main @ 3962fea, H3: real Moon-wide, polar still stub) · A3 merged to main at M3 (see Done log).
- Done: A0–A3. Real data merged; filters, sorts (price ↑↓, viability, Sun Score, Signal Score), D-6 e2e, MAP-5 hover label, reviewer pass (no blocking). vitest 17, e2e 12, CI green.
- Next: A4 — `science/*.ts` mirror (geometry, visibility) + parity tests vs `pipeline/tests/golden/golden_v1.json` (use `parity-checker`), merge H4 (polar real data + horizons), South Pole tier polish, **3D Tour** (plan mode first). Read spec §3.3, §3.6, §6.5, §7. Blocked on H4 for polar/tour; geometry/visibility parity can start now.
- Blockers: H4 (polar). Open for Pipeline: R-A2 (why/blurb/nearest feature), R-A3 (glossary.json), R-A4 (manifest still says contract_version 1 + stub:true), R-A5 (basemap 9 MB → smaller/ small variant).
- Known gaps: OV-7 comm window, OV-3 min/mean/max toggle, Home type + "More" filters (A5), Rent tab/time slider (A6; D-6 test has a TODO to add them); cards show "Plot #i" not the real id/badges (RES-2, A5); results flicker once on tier switch (null-rect query then rect query); PriceInput min>max gives 0 results with no hint; basemap blob URL flashes for one render after tier switch.
- Perf (real data, M3 GPU): first card ≈ 0.3 s; software-GL headless ≈ 3 s (was 5 s). Filter+sort ≈ 10 ms/64.8k rows. Software GL also loses deck.gl taps at fit zoom (picking readback > 250 ms) → map click now selects the hovered plot (hover picking is reliable).
- ASSUMED: plot half-size global 0.5°/polar 480 m; price bands = quantiles of UNFILTERED prices; pills at fit+3 zoom (cap 1500); dots scale with zoom (≥0.8 px), fade under overlay, picking radius 5 px; list excludes off-market always; any price bound hides off-market plots on the map; "Hide off-market" hides grey rings.
- e2e notes: runs against `vite build && preview` (4173); expect timeout 15 s, test timeout 60 s (software GL slow). Pill-click and dot-click tests use fixed geometry (1200×700 / 1400×800).
- Commands: `cd app && npm ci`, `npm run dev`, `npm test`, `npm run lint`, `npx playwright test`, `npm run build`

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| A0 | ✅ (CI pending) | see git log | no | CI job blocked, Q-A1 |
| A1 | ✅ | see git log | no | stub data; worker + filters in A2/A3 |
| A2 | ✅ (OV-7 comm window deferred) | see git log | no | worker + overlays + tooltips |
| A3 | ✅ | see Done log | M3 | real data, filters, D-6 e2e, reviewer pass |
| A4 | ⬜ | | | |
| A5 | ⬜ | | | |
| A6 | ⬜ | | | |
| A7 | ⬜ | | | |

## Contract status
<!-- contract version I'm built against; mismatches seen; adaptations made -->

## Open questions
Q-A2: 14 Nov · First-load budget (3 s). Startup downloads ≈ 13 MB (basemap 9 MB + cols 4 MB); list is interactive in ~0.3 s on a GPU locally but 9 MB over a slow link may exceed 3 s. ASSUMED: acceptable for the demo (static host, brotli doesn't help JPEG); asked Pipeline for a smaller basemap (R-A5). Humans: is a ~13 MB first load OK, or should I lazy-load the basemap further / require a smaller JPEG?
<!-- Q-A#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
Q-A1: human granted App Claude permission to write the app CI workflow → `.github/workflows/app.yml` (app/** paths only: lint, tsc, vitest, build, Playwright). Pipeline's job is not in this file. · chat · 14 Nov
<!-- Q-A#: answer · source · date -->

## Requests to Pipeline Claude
R-A4 (14 Nov, after H3): `app/public/data/manifest.json` still says `contract_version: 1` + `stub: true` (tiers: global real, polar stub) while CONTRACT.md says v2. Please bump the manifest field with the data (I built against v2; loader warns on mismatch; my loader test only asserts ≥ 1 until fixed).
R-A5 (14 Nov): first-load weight. `global/basemap.jpg` is now 9.0 MB (hillshade 8192×4096) + 4.1 MB cols.bin ≈ 13 MB at startup. Please consider (a) a smaller JPEG quality/size for the main basemap and/or (b) a `basemap_small.jpg` (~2048×1024) I can show first and for card thumbnails. Not blocking: with a real GPU the list is interactive in ~0.3 s locally; the basemap loads after the list.
R-A3: export `config/glossary.json` (D-1: tooltip text per term with optional `formula`/`source`) and copy it to `app/public/data/glossary.json` (or tell me where). Ids I use: sunlight, longest_night, earth_contact, longest_blackout, temperature, slope, land_type, ice, viability, landing, sun_score, signal, comfort, views, ice_score. Until then I use an app-side fallback (`src/ui/glossary.ts`).
R-A2: listing needs a one-line 'why' (DET-2) and nearest named feature (DET-1) per plot — add to detail records `{why, nearest_feature, nearest_km}` by H3 (additive). Until then the listing shows plot number and the stub blurb.
R-A1 (RESOLVED: names are s_safety,s_power,s_comms,s_thermal,s_landmark,s_ice; cols.json keys confirmed from stub): confirm exact names of the six `s_*` score columns (spec §5 says `s_safety … s_ice`); I assumed s_safety,s_power,s_comms,s_thermal,s_terrain,s_ice. Also confirm `cols.json` schema keys (`rows`, `columns[{name,dtype,offset,scale}]`).
<!-- R-A#: what I need (field, format, fix) · why · by when -->

## Replies to Pipeline Claude
<!-- reply to R-P#: … -->

## Done log
- 14 Nov · A3 done · merged H3 (contract v2); real detail fields (id, nearby, P90 slope, buildable area, energy, landing safe); shared basemap blob (1 download), map mounts after first results; Sun/Signal Score sorts; reviewer fixes: "Showing 200 of N", MAP-5 "Off market: not safe to land" hover label, price filter hides off-market plots, band-edge memo, store selectors, detail-tile retry on non-404, worker onerror rejects pending, formatPrice rollover, Escape ignored in inputs, memoised deck data + picking radius + click-selects-hover, D-6 test now filters to ~top-price plots · vitest 17, e2e 12
- 14 Nov · A3 prep · filters (price/land/hide-off), query lifted to App+store, map mask, D-6 e2e, perf check · vitest 17, e2e 10
- 14 Nov · A2 · overlays (6 names, legend, opacity), compute worker (filter/sort), glossary tooltips; fixed deck.gl null-image overlay error and dots hiding overlay · vitest 13, e2e 8
- 14 Nov · A1 done · listing shell (header, price+facts, scores, facts, fine print, notice), Back/Escape · e2e 6 passed
- 14 Nov · A1 (part) · results list + sort + hover link + 2-col layout · vitest 10, e2e 4, lint/tsc clean
- 14 Nov · A1 (part) · MapView + markers + selection store · vitest 8, e2e 2, lint/tsc clean
- 14 Nov · A1 (part) · loader + types vs contract v1 · vitest 5 passed, lint/tsc clean
<!-- newest first: date time · WP · what · sha · tests -->
