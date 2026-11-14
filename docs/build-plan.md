# Lunar Listings — Build Plan (task level)

*NASA Space Apps Challenge 2026 · Team afc-spaceapps · v1.0 · 14 Nov 2026*

*Turns `docs/milestones.md` (what each milestone delivers) and `docs/technical-spec.md` (how) into **small, ordered tasks** for a **48-hour** event with **4 people**. Times are hours from kickoff. If your event is longer or shorter, scale the hour columns proportionally; the order and dependencies stay the same.*

**Who builds it:** two Claude Code agents (Pipeline Claude on computer 1, App Claude on computer 2) plus the humans. The agent-level split, git workflow, logs and kickoff prompts are in `docs/agents/` (start with `docs/agents/PLAN.md`). Roles A and B below map to **Pipeline Claude**; F maps to **App Claude**; P stays with the **humans** (presentation, decisions, novice test).

**Decisions locked for this plan:**
- **Stack:** Python 3.11 pipeline (NumPy, Numba, rasterio) + React/TypeScript/Vite + deck.gl frontend, static hosting.
- **Earth contact rule:** `terrain_margin`. Earth counts as visible when it's at least 1° above the local terrain horizon (spec §3.6).

---

## 1. Roles

| Role | Track | Owns | Backup for |
|---|---|---|---|
| **A — Geometry** | Data A | Ephemeris, Sun/Earth geometry, horizons, visibility stats, Horizons validation, TypeScript science mirror | B |
| **B — Terrain & scoring** | Data B | DEMs, slopes, grids, temperature, land/ice/landmarks, scoring, pricing, export | A |
| **F — Frontend** | Frontend | App shell, map, results, listing, 3D Tour, Rent, modes | P |
| **P — Presentation + integration** | P (+ helps F) | Story, assets, stub data QA, docs, project page, video, deck; then second frontend dev | F |

**Rules**
- Tasks are 1–3 h. A task is done only when its **Done when** check passes and it's pushed to `main` (or merged from a short branch).
- Never wait: if a dependency is late, build against the stub data or golden files.
- Each milestone ends with a git tag (`m0`…`m8`) and a 3-line note in `docs/progress.md`.

## 2. Sync points

Ten minutes, everyone, standing.

| Hour | Sync | Decide |
|---|---|---|
| 0 | Kickoff | Roles; M0 decisions; start downloads |
| 2 | **M0 gate** | Data format frozen; stub data merged |
| 7 | M1 gate | Skeleton UI on stub; ephemeris + DEMs in hand |
| 13 | **M2 gate** | Horizons validation passed? (if not, A fixes first; nothing scales until it passes) |
| 19 | **M3 gate ★** | Real Moon-wide map live; first demo recorded |
| 24 | Check-in | Polar horizons on track? If not by hour 30 → simplified-lighting fallback |
| 28 | **M4 gate (MVP)** | South Pole + 3D Tour live; MVP recorded |
| 36 | M5/M6 gate | Feature freeze for anything not started |
| 41 | **M7 gate** | Freeze; only fixes from here; video cut starts |
| 46 | Submit | Submit with ≥ 1 h buffer |

## 3. Critical path

```
A1 ephemeris ─▶ A3 geometry ─▶ A5 smooth-Moon stats ─▶ A6 validation ─▶ B9 scoring ─▶ B11 export ─▶ F10 real data (M3 ★)
B2 polar DEM ─▶ A8 horizons ─▶ A9 terrain-aware stats ─▶ B13 polar export ─▶ F13 South Pole + 3D Tour (M4 MVP)
```

The polar horizons (A8) are the riskiest task. A starts them as soon as M2 passes, and B takes over scoring and export so A can stay on them.

---

## 4. Tasks by milestone

**Est** = estimated hours. **Dep** = task IDs that must be done first.

### M0 — Setup & contract (hours 0–2)

| ID | Who | Task | Est | Dep | Done when |
|---|---|---|---|---|---|
| S1 | All | Kickoff: confirm roles, decisions in `requirements.md` §13 (name, year 2028, grid sizes, polar core 85–90°S), write them into `config/lunar-listings.yaml` | 0.5 | — | Config committed; README names the decisions |
| S2 | B | Start DEM downloads (global LOLA 118 m; PGDA `LDEM_80S_80MPP`, `LDEM_80S_20MPP`, `LDSM_80S_20MPP`, hillshade) into `data/raw/`; record SHA-256 | 0.3 | — | Downloads running; `sources.yaml` lists URLs |
| S3 | A | Repo scaffold: `pipeline/` package, `pyproject.toml`, `Makefile`, pytest, ruff | 1 | — | `make test` runs an empty suite |
| S4 | F | App scaffold: Vite + React + TS + deck.gl + zustand + react-window; ESLint; Vitest; Playwright | 1 | — | `npm run dev` shows a blank map canvas |
| S5 | B+F | **Freeze data formats** (spec §5): `cols.json` schema, detail record, horizon tile layout, manifest | 1 | S1 | `docs/technical-spec.md` §5 marked "frozen v1" |
| S6 | P | Write `stub.py`: ~50 fake plots per tier in the frozen formats + fake ephemeris + placeholder basemaps | 1.5 | S5 | `make stub` fills `app/public/data/`; F can load it |
| S7 | A | Hand-test the Horizons sub-point query and one `coord@301` query; save responses | 0.5 | — | Two raw responses saved in `data/cache/` |
| S8 | P | Story agreed (presentation.md §1–2); `docs/presentation/` folders; CI workflow (lint + tests) | 0.5 | S3,S4 | CI green on `main`. **Tag `m0`.** |

### M1 — Skeleton + raw data (hours 2–7)

| ID | Who | Task | Est | Dep | Done when |
|---|---|---|---|---|---|
| A1 | A | `fetch/horizons.py` + `ephemeris.py`: full-year hourly query, parse incl. the longitude-sign line, unit vectors, TSI; commit `ephemeris_2028.csv` | 2.5 | S7 | 8,784 rows; TSI within 1320–1412 (test) |
| A2 | A | `geometry.py`: ENU frame, az/el, Earth parallax, pole convention + unit tests | 2 | S3 | Geometry tests pass |
| B1 | B | `terrain.py` global: resample to 1/32°, slope (latitude-aware), roughness, relief | 2.5 | S2 | Rasters in `data/work/`; slope sanity (maria flat, crater walls steep) |
| B2 | B | Polar: crop 20 m DEM + slope to the core area; build the 80 m far-field mosaic; 240 m cell grid with `safe_frac_cell` | 2 | S2 | Arrays saved; a cell count matches the config |
| F1 | F | `data/loader.ts`: manifest, `cols.bin` → typed arrays, lazy tile fetch + cache | 1.5 | S6 | Unit test decodes stub columns |
| F2 | F | `MapView`: two tiers (equirect / polar) with basemap `BitmapLayer`, pan/zoom, tier switch | 2 | S4,F1 | Both stub basemaps render; tab switches |
| F3 | P→F | Markers: dots when zoomed out, price pills when zoomed in, grey Off-market dots (MAP-2, MAP-5) | 1.5 | F2 | Zooming swaps dots ↔ pills on the stub |
| F4 | P→F | Results list (virtualized, capped, "N results", Price sort) + listing card with facts line | 1.5 | F1 | 200-card cap works; hover highlights pin |
| F5 | F | Listing panel shell: header, price, facts line, facts, "← Back to results", fine-print disclaimer | 1 | F4 | Click pin/card → listing → back. **Tag `m1`.** Screenshot → `docs/presentation/m1/` |

### M2 — Geometry validated + Moon-wide systems (hours 7–13)

| ID | Who | Task | Est | Dep | Done when |
|---|---|---|---|---|---|
| A3 | A | `visibility.py` (Numba): per plot/hour Sun and Earth el/az, disk fraction, `earth_ok` (terrain_margin), run-lengths | 2.5 | A1,A2 | Equator: 50% sunlit, ~355 h night (test) |
| A4 | A | Stats: sunlit_frac, energy, longest dark/light, Earth %, longest blackout, monthly arrays, run lists | 1.5 | A3 | Near side ≈ 100% Earth, far side ≈ 0% (test) |
| A5 | A | **`validate.py` (EPH-3):** Horizons `coord@301` at near side, limb, south pole × 3 dates; report + plot | 1.5 | A3 | Errors ≤ 1° smooth / ≤ 0.1° with parallax at polar sites; `docs/validation.md` + `img/validation.png` |
| B3 | B | `thermal.py` T1 + thermal hazard | 1 | A4 | Equator ≈ 390 K day / 95–100 K night (test) |
| B4 | B | `plots.py` global grid (64,800), area_km², aggregate SAFE: slope mean/P90, safe fraction, roughness, relief, `landing_safe`, `hazard_score` | 2 | B1 | Every plot has SAFE fields; steep crater walls → Off market |
| B5 | B | Sanity suite skeleton (pytest on real outputs) | 1 | A4,B3 | All §9 Moon-wide checks run in CI when data is present |
| F6 | F | Overlay plumbing: overlay `BitmapLayer` + legend + opacity slider; worker scaffold (`compute.worker.ts`) | 2 | F2 | Stub overlay toggles; worker round-trip works |
| F7 | P | Tooltip/glossary system (`config/glossary.json`) + fine-print component | 1 | F5 | Every fact has a tooltip. Validation plot → `docs/presentation/m2/`. **Tag `m2` when A5 passes.** |

> **Gate:** if A5 fails, A fixes it before starting A8. B keeps going on B6–B10.

### M3 — Real Moon-wide map ★ (hours 13–19)

| ID | Who | Task | Est | Dep | Done when |
|---|---|---|---|---|---|
| B6 | B | `land.py`: land types (global rules), landmarks (gazetteer + Apollo + Artemis III), nearby list, landmark score | 2 | B4 | Every plot has a land type; Apollo plots list nearby sites |
| B7 | B | `scoring.py`: normalization, penalties, sub-scores, viability, named scores, Off-market cap | 1.5 | A4,B3,B4 | Determinism + monotonicity tests pass |
| B8 | B | `pricing.py`: Moonstimate (BASE 5,000, k 6.9), range, `rent_avg`, scarcity cutoff into config, badges, blurb templates | 1.5 | B7 | Price spans ~$5K → ~$5–10M; RENT-5 test passes |
| A6 | A | `best_window` for Lander pad / Habitat from run lists; **gate calibration script** (counts per gate value) | 1.5 | A4 | Script prints results per type; values chosen and written to config |
| B9 | B | `export.py` global: `cols.bin`/`cols.json`, detail tiles, overlay PNGs + legends, basemap image, manifest | 2 | B6–B8 | `make data` replaces the stub for the Moon-wide tier |
| A7 | A | Golden vectors v1 (geometry, visibility, stats, scoring) → `pipeline/tests/golden/` | 1 | A4,B7 | Files committed; schema frozen |
| F8 | F | Switch to real Moon-wide data; facts line, why line, Off-market, Price filter, Price/Viability sort; zoom performance check | 2 | B9 | 64,800 plots pan/zoom smoothly; filter < 200 ms |
| F9 | P | Overlays OV-1…OV-5 wired to real PNGs; e2e test "Buy price never changes with filters/sort" | 1.5 | B9,F6 | Playwright test green. **Tag `m3` ★**; record demo steps 1–3 → `docs/presentation/m3/` |

### M4 — South Pole District: MVP (hours 19–28)

| ID | Who | Task | Est | Dep | Done when |
|---|---|---|---|---|---|
| A8 | A | **`horizons.py` (Numba):** ray-march at plot resolution (960 m), curvature, near/far DEM, 180 azimuths, uint8 quantization; synthetic-cone test | 4 | A5,B2 | Cone test ≤ 0.05°; full core area computed; cached |
| A9 | A | Terrain-aware visibility + stats for polar plots (reuse A3/A4 with horizons) | 1.5 | A8 | Shackleton floor ≈ 0% sunlit; lit rims in the top tier |
| A10 | A | HOR-2 cross-check vs. a Moon Trek/Quickmap profile for one site; note in `docs/validation.md` | 0.5 | A8 | Comparison recorded |
| B10 | B | Polar plots: aggregation, best cell, PSR mask, ice distance (EDT), polar land types, scoring/pricing reuse | 2 | A9,B2 | Polar plots have all fields incl. `ice_km` |
| B11 | B | Polar export: `cols.bin`, detail tiles, **horizon tiles for every plot**, polar overlays, polar basemap from PGDA hillshade | 2 | B10 | `make data` produces polar outputs within the size budget |
| F10 | F | South Pole tier on real data: projection helpers, markers, overlays, selection | 2 | B11 | Tier switch shows real polar plots |
| F11 | F | **3D Tour** (`TourCanvas`): horizon silhouette, Sun/Earth paths (worker-computed), current markers, countdown to sunset/Earthset, vertical-scale label | 3 | A7,B11 | Tour renders for any polar plot; countdown matches the Python reference on golden data |
| F12 | P | `science/*.ts` mirror (geometry, visibility) + **parity tests** vs. golden vectors | 2 | A7 | Vitest parity green. **Tag `m4` — MVP**; record the 3D Tour hero clip → `docs/presentation/m4/` |

> **Fallback (hour 30):** if A8/A9 aren't done, B ships the polar tier with simplified lighting (`m = 0`, labeled), F shows a flat-horizon 3D Tour, and everyone moves on to M7/M8.

### M5 — Listings come alive (hours 28–36, parallel with M6)

| ID | Who | Task | Est | Dep | Done when |
|---|---|---|---|---|---|
| F13 | P | Home type filter (gates from `bw_*` + static facts) + match % + Best-match sort (worker) | 2 | F8,A6 | Each type returns ≥ min results; prices unchanged |
| F14 | P | Named scores panel, badges (≤ 2 per card), Moonstimate range, blurb, Nearby list | 1.5 | F8 | Listing matches the v2.2 layout |
| F15 | P | Land type filter, "Hide off market" toggle, "Plots for you" featured cards, solar power overlay (OV-11), ice overlay (OV-8) | 1.5 | F8,B11 | All toggles work on both tiers |
| B12 | B | Blurb template polish, featured-plot picks (polar rim, far-side bargain, Apollo-adjacent), Diviner cross-check note (TEMP-4) | 1.5 | B11 | Featured IDs in config; `docs/validation.md` updated. Capture "Habitat vs. Ice depot" → `docs/presentation/m5/` |

### M6 — Time & Rent (hours 28–36, parallel with M5)

| ID | Who | Task | Est | Dep | Done when |
|---|---|---|---|---|---|
| A11 | A | `science/rent.ts` + stats over a window (mirror of `pricing.py`); parity vectors for rent | 2 | F12 | Parity green; RENT-5 holds in TS |
| F16 | F | Buy/Rent tabs; move-in + stay controls; Rent pins = `rent_avg`; listing shows /mo + total + change reason + Price cut badge | 2.5 | A11 | Moving in +2 weeks changes rent, not Buy price (e2e) |
| F17 | F | Rent history chart (12 one-month stays); time slider; OV-7 live comm window; tour follows slider | 2 | A11,F11 | ≥ 15 fps scrubbing on a laptop |
| A12 | A | Find the demo's **before/after number** (a rim plot whose rent drops when moving in 2 weeks later) and log it | 0.5 | F16 | Number and plot ID in `docs/presentation/m6/notes.md`. **Tag `m6`** |

### M7 — Trust, polish & demo mode (hours 36–41)

| ID | Who | Task | Est | Dep | Done when |
|---|---|---|---|---|---|
| F18 | F | Demo mode (`?demo=1`: offline data, preset buttons for the 6 demo steps) + presentation mode (`?present=1`) | 2 | F16,F17 | Full demo runs with Wi-Fi off |
| F19 | P | "About the data", "Formulas", "Validation" views; data credits; accessibility pass (focus, labels, colorblind check) | 2 | F14 | Every metric shows units + source |
| B13 | B | Performance pass (payload sizes vs. budget, lazy tiles, compression); deploy to GitHub Pages | 1.5 | F18 | Public URL loads < 3 s; total within budget |
| A13 | A | **Novice test** with 3+ people outside the team; log findings; fix the top 2 | 1.5 | F18 | Notes + quote in `docs/presentation/m7/` |
| P1 | P | README: setup, `make` commands, architecture figure, data sources, limits | 1 | — | README complete. **Tag `m7`** |

### M8 — Freeze & submit (hours 41–48)

| ID | Who | Task | Est | Dep | Done when |
|---|---|---|---|---|---|
| X1 | All | **Feature freeze.** Bug bash: run the §11 demo script twice on the deployed build with Wi-Fi off | 1 | m7 | Zero blocking bugs |
| X2 | P | Cut the **30 s video** from milestone clips (presentation.md §2), captions, real numbers | 3 | A12,X1 | ≤ 30 s, uploaded, link public |
| X3 | F | Replace deck mockups with real screenshots; fill the links and team names; export the deck | 1.5 | X1 | 7 slides final, link public |
| X4 | A+B | Project page text (presentation.md §5); NASA datasets and how they're used | 1 | X1 | Page drafted in the submission form |
| X5 | All | Backup recordings of every demo step; test all links in a private window; **submit by hour 46** | 1 | X2–X4 | Submission confirmed. **Tag `m8`** |

---

## 5. Per-person timeline (48 h view)

| Hours | A — Geometry | B — Terrain & scoring | F — Frontend | P — Presentation/integration |
|---|---|---|---|---|
| 0–2 | S3, S7 | S1, S2, S5 | S4, S5 | S6, S8 |
| 2–7 | A1, A2 | B1, B2 | F1, F2, F5 | F3, F4 |
| 7–13 | A3, A4, **A5** | B3, B4, B5 | F6 | F7 |
| 13–19 | A6, A7 | B6, B7, B8, B9 | F8 | F9 |
| 19–28 | **A8**, A9, A10 | B10, B11 | F10, F11 | F12 |
| 28–36 | A11, A12 | B12 | F16, F17 | F13, F14, F15 |
| 36–41 | A13 | B13 | F18 | F19, P1 |
| 41–48 | X1, X4, X5 | X1, X4, X5 | X1, X3, X5 | X1, X2, X5 |

Sleep: stagger 3–4 h blocks. A sleeps after A5 (≈ h 13–16), F after F8 (≈ h 19–22), B after B11 (≈ h 28–31), P after F15 (≈ h 34–37). Nobody sleeps through a gate they own.

## 6. Cut list (if behind, cut from the bottom up)

| Order | Cut | Effect |
|---|---|---|
| 1 | Rent history chart, OV-7, play/pause | Rent tab still works |
| 2 | Ice overlay, solar overlay, land-type filter | Fewer overlays |
| 3 | Badges and blurbs | Plainer cards |
| 4 | Home type + match % | Sort by price/viability only |
| 5 | Rent tab | Video ends on the 3D Tour (backup script) |
| 6 | Terrain-aware horizons → simplified lighting | Last resort; weakens the south-pole story |

Never cut: the M0 format freeze, Horizons validation (A5), offline demo mode (F18) or the M8 block.
