# Lunar Listings — Final Milestones

*NASA Space Apps Challenge 2026 · Team afc-spaceapps · v2.0 (final) · 14 Nov 2026*

*Builds `docs/requirements.md` v2.0. Merges the team's build order (requirements draft v0.1, §9.2) with milestones v1.0. Earlier versions are in `docs/archive/`.*

![Build plan](img/roadmap.png)

---

## 1. How we build

- **Stub first, then make it real.** In M0 we freeze the `plots.json` data contract and write a **stub file with fake data**. The interface team builds against the stub from hour one while the data team makes it real. Nobody waits for anybody.
- **Vertical slices.** Every milestone ends with something that runs and has been checked, tagged in git (`m0`, `m1`, …) with a 3-line note in `docs/progress.md`.
- **Validate before scaling.** Sun and Earth geometry is checked against JPL Horizons (M2) before the whole Moon is priced.
- **Always demoable from M3.** Later milestones make the demo better; none of them create it.
- **One-shot generation is allowed** for any module. It must pass that milestone's exit criteria, the same as hand-written code.
- **Capture presentation assets at every milestone** into `docs/presentation/mN/`.
- **Cut line.** If time is short, stop at the last passed milestone and polish. P2 work starts only after M4 passes.

## 2. Tracks

| Track | Owner **[TBD]** | Covers |
|---|---|---|
| **Data A — geometry** | | EPH, SOL, COMM, HOR (polar lighting) |
| **Data B — terrain & scoring** | | GRID, SAFE, TEMP, LAND, ICE, VS, PRICE |
| **Frontend** | | UI, MAP, DET, FIL, OV, TIME, SCN |
| **Presentation (P)** | (shared; one named owner) | Story, assets, demo mode, video, slides, project page |

---

## 3. Overview

| # | Milestone | What exists at the end | Pri |
|---|---|---|---|
| **M0** | Setup & contract | Repo, decisions, data contract + stub data, downloads started | P0 |
| **M1** | Skeleton + raw data | App shows map, fake price markers and listing panel; ephemeris cached; DEM downsampled | P0 |
| **M2** | Geometry + Moon-wide systems | Validated Sun/Earth geometry; Systems A–D for every global plot; sanity checks pass | P0 |
| **M3** | Real Moon-wide map ★ | Real prices on the global map; overlays; price filter; listing panel with real facts | P0 |
| **M4** | South Pole District (MVP) | Terrain-aware polar lighting and comms; polar plots; sky view | P0 |
| **M5** | Listings come alive | Blurbs, land types, landmarks, nearby, ice access, price history, presets, featured listings | P1 |
| **M6** | Time & move-in date | Time slider, comm-window overlay, move-in date re-pricing | P1 |
| **M7** | Trust, polish & demo mode | About/formulas/validation pages, disclaimer, demo and presentation modes, novice test | P0/P1 |
| **M8** | Freeze & submit | Rehearsed demo, 30 s video, 7-slide deck, project page, submission | P0 |
| *Stretch* | P2 lane | Ask the realtor (AI), compare, adjustable weights, relay toggle, T2 heat model | P2 |

★ = demoable from here on. **MVP = M0–M4 + M7 (disclaimer, demo mode) + M8.**

```
M0 ─▶ M1 ─▶ M2 ─▶ M3 ─▶ M4 ─┬─▶ M5 ─┐
       (UI on stub data)     ├─▶ M6 ─┼─▶ M7 ─▶ M8
                             └─▶ P2 lane (only after M4)
```

---

## 4. Milestone details

### M0 — Setup & contract (everyone)

**Exit criteria:**
- [ ] Repo structure: `pipeline/`, `app/`, `data/` (gitignored large files), `docs/`. README skeleton.
- [ ] Open questions §13 decided: name, analysis year, grid sizes, polar core area, cutoff, preset values.
- [ ] **`plots.json` data contract frozen** (requirements §10), plus a **stub file with ~50 fake plots** (global and polar).
- [ ] Horizons queries verified by hand: one sub-point query and one topocentric `coord@301` query.
- [ ] DEM downloads started (global LOLA + PGDA south-polar).
- [ ] Map library chosen.
- [ ] **P:** story agreed (`docs/presentation.md`); `docs/presentation/` created.

### M1 — Skeleton + raw data (parallel)

**Exit criteria:**
- [ ] **Frontend:** basemap with pan and zoom; price markers from the stub; click → listing panel (stub facts); South Pole tab; disclaimer shown. *(UI-1/2/3, MAP-1–4, DET-1–4 on stub)*
- [ ] **Data A:** ephemeris cache for the analysis year: sub-solar and sub-Earth points, Sun and Earth range, hourly, committed. *(EPH-1, EPH-4)*
- [ ] **Data B:** global DEM downsampled; slope, roughness and relief rasters; polar DEM cropped. *(SAFE inputs)*
- [ ] **P:** screenshot of the skeleton UI (for the "how we built it" record).

### M2 — Geometry + Moon-wide systems (Data A + B)

**Exit criteria:**
- [ ] **Validation:** EPH-3 passes (≤ 1° smooth method; ≤ 0.1° with parallax at polar sites), at near-side, limb and south-pole sites.
- [ ] Systems A–D computed for every global plot: SAFE, SOL (TSI, sunlit, energy, longest dark), TEMP (T1), COMM.
- [ ] Sanity checks automated and passing: near side ≈ 1.0 contact, far side ≈ 0; equator ≈ 0.5 sunlit and ~355 h night; TSI 1320–1412; T1 ≈ 390 K / 95–100 K.
- [ ] **P:** validation plot saved (ours vs. Horizons), for slide 5.

### M3 — Real Moon-wide map ★ (all)

**Exit criteria:**
- [ ] Viability and Moonstimate computed (VS-1–3, VS-5, PRICE-1/2) and written to `plots_global.json`.
- [ ] The app runs on real data: price markers, listing panel with real facts and the "why" line, price filter (FIL-1).
- [ ] Overlays OV-1 to OV-5 with legends and colorblind-safe palettes.
- [ ] Demo steps 1–3 (requirements §11) work.
- [ ] Tagged `m3`; screen recording saved.
- [ ] **P:** capture the near side vs. far side contrast with the Earth-contact overlay.

### M4 — South Pole District: MVP (Data A + B + Frontend)

**Exit criteria:**
- [ ] Terrain horizons computed for polar analysis cells (HOR-1); one horizon cross-checked (HOR-2).
- [ ] Polar SOL, COMM and TEMP use terrain-aware visibility (SOL-2, COMM-4).
- [ ] `plots_polar.json` with ~1 km plots; polar overlays.
- [ ] **Sky view** on the polar listing: horizon, Sun and Earth paths, time to next sunset and Earthset (DET-5).
- [ ] Sanity checks: Shackleton floor ≈ 0 sunlit; known lit rims and ridges in the top tier; steep walls "Not buildable".
- [ ] Demo steps 4–5 work. **MVP reached.**
- [ ] **P:** hero clip of the Sun skimming the horizon in the sky view; capture of the polar sunlight overlay (peaks glowing, PSRs black).

### M5 — Listings come alive (Data B + Frontend)

**Exit criteria:**
- [ ] Listing blurbs from templates (DET-6).
- [ ] Land types (LAND-1) and land-type filter (FIL-2).
- [ ] Landmark layer with Artemis III regions and Apollo sites (MAP-6, LAND-2/3); nearby list (DET-9).
- [ ] Ice access (ICE-1/2, OV-8).
- [ ] Price history chart (DET-7).
- [ ] "Shopping for" presets (FIL-4) re-price the map.
- [ ] Featured listings in the empty panel (UI-5).
- [ ] **P:** capture "same Moon, different shoppers": Home base vs. Ice depot maps.

### M6 — Time & move-in date (Data A + Frontend)

**Exit criteria:**
- [ ] Time slider (TIME-1/2) and comm-window overlay (OV-7) at ≥ 15 fps.
- [ ] Sky view follows the slider.
- [ ] **Move-in date** (SCN-1) re-prices the selected plot, with a highlighted explanation of the change.
- [ ] Ties labeled (VS-4).
- [ ] Demo step 6 works.
- [ ] **P:** find the real **before/after number** for the video ("arrive 2 weeks later → price ↓ X%").

### M7 — Trust, polish & demo mode (Frontend + P)

**Exit criteria:**
- [ ] About the data, Formulas, and Validation views; every metric has units and source (DET-8, NFR-8).
- [ ] Disclaimer in place (UI-3).
- [ ] **Demo mode** loads featured plots and scenarios offline (PRS-2, NFR-5).
- [ ] *(P1)* Presentation mode (PRS-3).
- [ ] Novice test: 3 people from outside the team each find a plot's price and 3 facts in ≤ 30 s, and explain one "why".
- [ ] Performance targets met (NFR-1/2).
- [ ] **P:** quote or observation from the novice test.

### M8 — Freeze & submit (all, led by P)

**M8a — Freeze & harden (~40%):**
- [ ] Feature freeze.
- [ ] Full demo script rehearsed twice on the deployed build, with the network off.
- [ ] README: setup, one-command pipeline, run, architecture, data sources.
- [ ] All P0 requirements verified.

**M8b — Present & submit (~60%):**
- [ ] 30 s video cut per `docs/presentation.md`: captions on, NASA datasets named on screen, real numbers.
- [ ] 7-slide deck finalized with real screenshots replacing placeholders.
- [ ] Project page: premise, what it does, NASA data and how it's used, validation, limits, roadmap, links.
- [ ] All links tested in a private window.
- [ ] Backup recordings stored.
- [ ] Submitted at least 1 hour before the deadline.

### Stretch (P2 lane, only after M4)

Ask the realtor (AI) · compare two plots · adjustable weights · relay toggle (SCN-2) · T2 heat-equation model · map search box · URL state · play/pause.

---

## 5. Time allocation

| M0 | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 |
|---|---|---|---|---|---|---|---|---|
| 5% | 10% | 12% | 12% | 18% | 10% | 8% | 10% | 15% |

**Example: a 48-hour event**

| Hours | Milestones |
|---|---|
| 0–2 | M0 |
| 2–7 | M1 |
| 7–13 | M2 |
| 13–19 | M3 ★ |
| 19–28 | M4 (MVP) |
| 28–36 | M5 and M6 in parallel |
| 36–41 | M7 |
| 41–48 | M8 (P starts cutting the video around hour 36) |

**Fallback:** if M4's terrain horizons aren't done by hour 30, ship the polar tier with simplified lighting (SOL-4), label it clearly, and go straight to M7 and M8.

## 6. Risks

| Risk | Mitigation | Where |
|---|---|---|
| Multi-GB DEM slow to download or process | Start in M0; downsample early; use the 80 m polar product first | M0–M1 |
| Horizons rate limits or downtime | A few sub-point queries total; cache and commit | M1 |
| Wrong geometry or reference frame | EPH-3 validation gate | M2 |
| Terrain horizons too slow | Smaller polar core area; fewer azimuths; precompute offline; SOL-4 fallback | M4 |
| Too many markers | Clustering by zoom; canvas/WebGL rendering | M1–M3 |
| Parody too close to Zillow branding | Original name, logo and colors; parody the layout only | M1 |
| "Selling the Moon" taken literally | Fictional-premise disclaimer; Outer Space Treaty line | M1, M7 |
| Prices feel arbitrary | Deterministic formula; why line; formulas page; sanity checks | M3, M7 |
| Network or AI down during judging | Offline demo mode; recordings | M7–M8 |
| Presentation squeezed | Assets captured every milestone; M8 is 15%; feature freeze | All |
| Scope creep | P2 only after M4; roadmap ideas go in `docs/roadmap-ideas.md` | All |
