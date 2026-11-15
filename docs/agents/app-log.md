# App Claude — log

*Single writer: **App Claude**. Others read only. Keep `## Resume here
- Branch: `app` (A4 work on `app-a4` worktree, pushed to `app`) · contract **v2**, main @ 8bc695e merged.
- Done (A4, mostly): `geo/geometry.ts`, `geo/projections.ts` (polar inverse), `science/visibility.ts` (series, stats, runs, best_window, countdown helpers) with **exact golden parity** (`science/visibility.test.ts`: angles 1e-6, stats 1e-9, runs/windows exact); **3D Tour** (`tour/*`, listing `Gallery` Photos | 3D Tour tab, polar only; canvas panorama, Sun/Earth 30-day paths, hollow = behind terrain, countdowns, own time slider until A6). e2e `tour.spec.ts`.
- R-A6 and R-A7 RESOLVED by Pipeline 8070ebc (real ephemeris.bin; quantisation golden fixed). Merged origin/main (6a7e75f); parity still exact; golden quantisation test un-skipped; new test checks ephemeris.bin vs CSV. vitest 34, e2e 14.
- Reviewer pass on A4 done (no blocking; fixed: tour waits for detail.best_cell_xy, primitive effect deps, hollow dots use series flags, wrap-around tests). DEFERRED: TIME-2 — Tour uses its own time slider; A6 must wire it to the global slider (owner: App, A6). Not done: memoising the series per plot, axis clip above 15°.
- A5 (in progress, on `app-a4`/`app`, NOT merged to main): Home type filter (gates via bw_lander_h/bw_habitat_h/sunlit/ice; polar-only ice depot hint), match % on cards, Best match sort (default when a type is chosen), More panel (min sunlight/Earth), real plot ids on cards (G-lat-lon / SP-row-col derived from x,y), badges (max 2 on cards: Hot property, Earth view, Peak of light, Off market), "Plots for you" strip (featured flag: best, cheapest, next best). vitest 38, e2e 17 (3 new in a5.spec.ts).
- ASSUMED: solar-farm gate = sunlit ≥ 60% only (safe_area_frac isn't a column, R-A8); match % uses only the weights listed per type in config (Σw·s/Σw); `Any` match = viability.
- Left for A5/A6: OV-11 Solar power overlay (needs R-A8 overlay PNG), Price cut badge (Rent tab, A6), named-score tooltips already done, FIL-6 URL state (P2), Tour↔global slider (TIME-2, A6), South Pole tier polish, tour memoisation.
- A7 (done on `app`, reviewer pass done, no blocking; NOT merged to main yet): `?demo=1` panel (far-side bargain, Earth overlay, pole sunlight, Shackleton + 3D Tour, rent shift on SP-0172-0148 + "+2 weeks"), `?present=1` (side panel/filters zoom ×1.35, bigger markers, opacity slider + debug tag hidden), About dialog (About / Formulas from glossary / Validation with the weak Diviner and Earth-fraction results stated; portal, focus trap, focus return), offline e2e (all requests same-origin), Pages `deploy` job in app.yml (push to main only; human enabled Pages: Actions). vitest 55, e2e 23.
- FLAKES: e2e on software GL is timing-sensitive after heavy specs (pill-click test, demo-scenarios test): each failed once in some full runs and passed alone/on rerun. Playwright `retries` = 1 on CI only (not local), trace on first retry. Pill test waits lengthened.
- Merged so far on main: through A6 (d0b39ac). A6/A7 deferred items: OV-7 comm-window overlay, Price cut badge on cards, RENT-4 per-window pins, SCN-2 relay, TIME-3 play, OV-11 (R-A8), South Pole tier polish, FIL-6 URL state, Q-A3 (home weights full vs delta).
- Next: human OK to merge A7 → main (M7; triggers first Pages deploy, base path /<repo>/); then deferred items by priority, or freeze (M8).
- POST-A7 polish (branch `app`, not merged): prettier map price pills (rounded, light border, per-band text colour); default view = random zoomed-in area (fit+5, ~40 plots, `?view=fit` for the whole map; 'Whole map' / 'Another area' buttons; empty-list hint). smoke + a5 e2e use `?view=fit`. vitest 59.
- MAKEOVER (branch `app`, not merged): black + baby blue (136,188,249) theme (`src/theme.css` variables; logo `public/logo.png` top-left in a `.topbar`, favicon from the crescent), segmented Buy/Rent + Photos/Tour tabs, glass panels, cards/listing as blocks, navy→baby-blue→white price-band ramp, tour canvas recoloured. Filter popovers now close on outside click/Escape (an open Land type popover covered the listing's Back button). Plot overview: cards say "Sunlit 51% of the year · Earth in view 0% of the year · 2° slope · 276.5 km²"; the listing shows labelled stat tiles. REMOVED the Rent history chart (DET-7 is therefore not implemented; user decision). e2e: pill test finds a pill via the map's pointer cursor instead of fixed coordinates. vitest 58, e2e 26.
- Commands: `cd app && npm ci`, `npm test`, `npm run lint`, `npx tsc -b`, `npx playwright test`, `npm run build`
- Earlier notes (A3) still apply: ASSUMED plot half-size, price bands, e2e geometry; known gaps OV-7, OV-3, Home type/More filters (A5), Rent (A6).

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| A0 | ✅ (CI pending) | see git log | no | CI job blocked, Q-A1 |
| A1 | ✅ | see git log | no | stub data; worker + filters in A2/A3 |
| A2 | ✅ (OV-7 comm window deferred) | see git log | no | worker + overlays + tooltips |
| A3 | ✅ | see Done log | M3 | real data, filters, D-6 e2e, reviewer pass |
| A4 | 🟡 parity ✅, tour ✅ (real ephemeris), reviewed ✅; polar polish pending | see git log | no | M4 (94204b7) |
| A5 | ✅ (OV-11 pending R-A8; Price cut badge in A6) | see git log | M5 | reviewer pass done |
| A6 | ✅ (OV-7, Price cut on cards, RENT-4 deferred) | see git log | pending OK | reviewer pass done |
| A7 | ✅ | see git log | pending OK | reviewer pass done |

## Contract status
<!-- contract version I'm built against; mismatches seen; adaptations made -->

## Open questions
Q-A3 (14 Nov): Home-type match % — is `config.home_types.<type>.weights` a FULL override (what I do: only the listed weights count, Σw·s/Σw) or a DELTA onto `config.weights` defaults (spec §6.8 says 'weight changes vs. defaults')? Default: full override. ASSUMED; humans/Pipeline please confirm.
Q-A2 (mostly resolved by P6 small basemaps; leaving for humans to close): 14 Nov · First-load budget (3 s). NOW: first paint needs cols 4.1 MB + small basemap 0.65 MB + JS ≈ 6 MB; the 8.2 MB full basemap loads in the background. Original text: Startup downloads ≈ 13 MB (basemap 9 MB + cols 4 MB); list is interactive in ~0.3 s on a GPU locally but 9 MB over a slow link may exceed 3 s. ASSUMED: acceptable for the demo (static host, brotli doesn't help JPEG); asked Pipeline for a smaller basemap (R-A5). Humans: is a ~13 MB first load OK, or should I lazy-load the basemap further / require a smaller JPEG?
<!-- Q-A#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
Q-A1: human granted App Claude permission to write the app CI workflow → `.github/workflows/app.yml` (app/** paths only: lint, tsc, vitest, build, Playwright). Pipeline's job is not in this file. · chat · 14 Nov
<!-- Q-A#: answer · source · date -->

## Requests to Pipeline Claude
R-A9 (14 Nov, FYI): `golden_rent_v1.json` sites (and the logged demo number SP-0172-0148 → $16,758 / $7,129) use premium 0, but the real plot carries a +75% landmark premium (Apollo + Peak of light), so the shipped `rent_avg` is ~1.75× the golden's 1-year rent. My TS parity is exact against the golden as written; the app scales from `rent_avg` so a 1-year stay equals it (RENT-5). Please either ship `premium` per plot (cols/detail) so the app doesn't have to infer it, or note that the demo numbers exclude it. Not blocking.
R-A8 (14 Nov): (a) add a `safe_area_pct` (0–100) column to both tiers so the Solar-farm gate (safe_area_frac ≥ 0.4) can run client-side; today only sunlit ≥ 60% is applied. (b) OV-11: add a `power` overlay (PNG+JSON legend, energy Wh/m²/day) for both tiers; `OVERLAY_NAMES` would gain `power`.
R-A6 (RESOLVED 8070ebc; was: blocks real 3D Tour): `app/public/data/ephemeris.bin` is still the v1 stub from `stub.py _ephemeris` (sun at t=0 = (0.9996,0,0.0269)). Please write the real one (float32 LE: sun_xyz[8784×3], earth_xyz[8784×3], earth_dist_m[8784], tsi[8784] from `ephemeris.load()`) in the real export and update manifest sha.
R-A7 (RESOLVED 8070ebc): `golden.py` `horizon_quantisation.cases` call `horizons.quantize(m)` with its default offset −3.0, but the file declares offset_deg −6 (and data uses −6). Pass `0.16, -6.0` so the cases match; I have the test skipped until then.
R-A4 (14 Nov, after H3): `app/public/data/manifest.json` still says `contract_version: 1` + `stub: true` (tiers: global real, polar stub) while CONTRACT.md says v2. Please bump the manifest field with the data (I built against v2; loader warns on mismatch; my loader test only asserts ≥ 1 until fixed).
R-A5 (14 Nov): first-load weight. `global/basemap.jpg` is now 9.0 MB (hillshade 8192×4096) + 4.1 MB cols.bin ≈ 13 MB at startup. Please consider (a) a smaller JPEG quality/size for the main basemap and/or (b) a `basemap_small.jpg` (~2048×1024) I can show first and for card thumbnails. Not blocking: with a real GPU the list is interactive in ~0.3 s locally; the basemap loads after the list.
R-A3: export `config/glossary.json` (D-1: tooltip text per term with optional `formula`/`source`) and copy it to `app/public/data/glossary.json` (or tell me where). Ids I use: sunlight, longest_night, earth_contact, longest_blackout, temperature, slope, land_type, ice, viability, landing, sun_score, signal, comfort, views, ice_score. Until then I use an app-side fallback (`src/ui/glossary.ts`).
R-A2 (RESOLVED at H6): listing needs a one-line 'why' (DET-2) and nearest named feature (DET-1) per plot — add to detail records `{why, nearest_feature, nearest_km}` by H3 (additive). Until then the listing shows plot number and the stub blurb.
R-A1 (RESOLVED: names are s_safety,s_power,s_comms,s_thermal,s_landmark,s_ice; cols.json keys confirmed from stub): confirm exact names of the six `s_*` score columns (spec §5 says `s_safety … s_ice`); I assumed s_safety,s_power,s_comms,s_thermal,s_terrain,s_ice. Also confirm `cols.json` schema keys (`rows`, `columns[{name,dtype,offset,scale}]`).
<!-- R-A#: what I need (field, format, fix) · why · by when -->

## Replies to Pipeline Claude
<!-- reply to R-P#: … -->

## Done log
- 14 Nov · A7 · demo/present modes, About dialog, Pages deploy job, offline e2e; reviewer fixes · vitest 55, e2e 23
- 14 Nov · A6 · scoring/rent TS + parity (224 cases), Buy/Rent tabs, time slider, Rent block + history + Price cut, tour on shared slider; reviewer fixes · vitest 55, e2e 18
- 14 Nov · A5 (part) · home type + match %, Best match sort, More filters, plot ids, badges, Plots for you · vitest 38, e2e 17
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
