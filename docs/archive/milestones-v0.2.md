# Lunar Landing Site Navigator — Development Milestones

*NASA Space Apps Challenge 2026 · Team afc-spaceapps · v0.2 · 14 Nov 2026*

*Companion to `docs/requirements.md` (v0.4). Requirement IDs refer to that document.*

*v0.2: added the Presentation track (P), asset capture at every milestone, and a detailed submission milestone.*

![Roadmap](img/roadmap.png)

---

## 1. Why milestones, and how they work

We build **module by module, in vertical slices**: get one thing working end to end, then widen. The reasons:

- **Every milestone ends in something runnable and checked.** A late failure costs one module, not the whole app.
- **Validation happens early.** If our Sun/Earth geometry is wrong, we find out at M2 (one site, compared against Horizons), not at the demo when 250k map cells look plausible but are wrong.
- **People can work in parallel.** Once the engine operations (ENG) are fixed, the UI, the agent and the data work proceed independently.
- **There's always a demo.** After M4 we always have a working demo. Later milestones only make it better.

**One-shot generation is still allowed**, for a whole module or for the whole app. The milestone structure is what makes it safe. Whether a module is hand-built or generated in one shot, it must:

1. be given the module's requirement IDs, its interfaces (requirements §10) and its exit criteria as the spec, and
2. pass the **same exit criteria** before it's accepted.

If a one-shot attempt covers several milestones at once, run all of their exit checks. If it fails, fall back to building module by module from the last passed milestone.

### 1.1 Rules for every milestone

- **Exit criteria are binary**: each passes or fails. A milestone is done only when all of them pass.
- **Every milestone ends with a commit tag** (`m0`, `m1`, …) and a 3-line note in `docs/progress.md`: what works, what was validated, known issues.
- **Do not start a milestone's "M" work until its dependencies have passed.** "S" and "C" items in other tracks can run in parallel.
- **Cut line:** if time runs short, stop at the last passed milestone and polish. Don't half-build the next one.
- **Capture presentation assets at every milestone** (PRS-10). Before tagging, save 1–3 clean screenshots or a ≤ 10 s clip of what now works to `docs/presentation/mN/`. Final assembly then becomes editing, not scrambling, and judges can see real progress.

---

## 2. Work tracks

| Track | Covers | Subsystems |
|---|---|---|
| **D — Data** | Fetching and preparing NASA data offline | EPH, TER, HOR, THM data, RES data |
| **E — Engine** | Runtime analysis and scoring | VIS, PWR, COM, THM, RES, EVL, MSN, SIT, ENG |
| **U — UI** | Everything the user sees | MAP, SKY, TML, CMP, SLP, EDU, EXP |
| **A — Agent** | AI Mission Agent and its interface | AGT, AUI |
| **P — Presentation** | Story, figures, demo mode, video, slides, project page | PRS, §12A |

Suggested owners for a 4-person team: one per track for D/E/U/A. Track A starts with engine support and becomes its own track at M3. **Track P has one named owner from M0** (alongside their other track). They own the story and the asset folder, and keep asking "how will this look on a slide?"

---

## 3. Milestone overview

| # | Milestone | Outcome | Priority | Depends on |
|---|---|---|---|---|
| **M0** | Foundations & decisions | Repo, tooling, closed TBDs, technical design doc | M | — |
| **M1** | Data foundation | NASA data fetched, documented, loadable | M | M0 |
| **M2** | Single-site geometry slice | Correct Sun/Earth az/el + horizon + visibility for catalog sites, validated against Horizons | M | M1 |
| **M3** | Single-site mission evaluation | Power, comms, terrain checks, score and ranking for the catalog sites; engine operations v1 | M | M2 |
| **M4** | Walking-skeleton UI ★ | First demoable app: pick a site, set a mission, sky view + timeline, Simple/Standard levels | M | M3 |
| **M5** | Grid scale & map | Whole-AOI overlays, red unusable areas, top-N; performance targets met | M | M3 (data), M4 (UI) |
| **M6** | Compare, date sweep & mission guidance | Side-by-side comparison; "what if we slip" heatmap; heuristics for a profile (binding constraint, sensitivity, seasons, terrain types) | S | M5 |
| **M7** | Thermal & resources | Diviner temperatures; PSR and cold-trap proximity | S | M5 |
| **M8** | AI Mission Agent | Goal → profile → grounded candidates + mission guidance, with a non-LLM fallback | S | M5, M6 (guidance), M7 (depot archetype) |
| **M9** | Explainer, Expert level & user testing | Explainer mode, Expert level, novice and concept-designer tests, accessibility, Assumptions & Sources page | S | M5 |
| **M10** | Hardening, presentation & submission | Full demo rehearsed, deployed, video, README, submission | M | All completed milestones |

★ = from here on we always have a demo.

**MVP line = M0 → M5 + M10.** If that's all we finish, we still meet the core of the brief.

### 3.1 Dependency and parallel-work view

```
M0 ─▶ M1 ─▶ M2 ─▶ M3 ─┬─▶ M4 ─┬─▶ M5 ─┬─▶ M6 ───────────────┐
                      │       │       ├─▶ M7 ─▶ M8 (agent) ──┤
                      │       │       └─▶ M9 ────────────────┼─▶ M10
                      │       │                              │
  (U track: UI scaffold, map base, sky-plot component from M1 onward, with mock data)
                      └─ (A track: archetypes, ENG schemas, prompt design, eval set from M3) ─┘
```

What can start early on mock data:
- **U track:** UI scaffold, polar map component, sky-plot and timeline components (from M1).
- **A track:** archetype table, ENG operation schemas, prompt drafts, evaluation-prompt set (from M3, against the single-site engine).

---

## 4. Milestone details

### M0 — Foundations & decisions

**Goal.** Everyone builds against the same decisions.

**Scope**
- Repo structure (`data-prep/`, `engine/`, `app/`, `agent/`, `docs/`), README skeleton, lint and test setup.
- Close TBD items #1–9 and #13 in requirements §13 (AOI extent, grid resolution, thresholds, default start date, normalization, PSR source). Close #10–12 by M8.
- **Write the technical design document**: architecture, languages and libraries, data formats, ENG operation signatures, frame and coordinate conventions.

**Exit criteria**
- [ ] TBDs #1–9 and #13 resolved and recorded in `requirements.md` (v0.3).
- [ ] Technical design doc reviewed by all team members.
- [ ] `docs/progress.md` created; CI (or a local test command) runs an empty test suite.
- [ ] **P:** story draft agreed (one-line pitch + the 30 s video outline in requirements §12A.3). Everyone builds toward the same demo moments. `docs/presentation/` created.

---

### M1 — Data foundation (Track D)

**Goal.** All core NASA data exists locally, documented and loadable by code.

**Requirements:** EPH-01–04, TER-01–03, TER-08, SIT-01, SIT-05, DAT-01–03, DAT-06–07, DAT-10–12, PLAT-04.

**Scope**
- Horizons ephemeris fetch script (2026–2030, 1 h) → stored file.
- LOLA DEMs (near and far field) plus slope and error maps for the AOI → cropped and stored.
- Site catalog file: the 9 Artemis III regions with coordinates and sources.
- Data README (source, version, resolution, license).

**Exit criteria**
- [ ] Rerunning the scripts from scratch reproduces the data products.
- [ ] Ephemeris covers the full span with no gaps (automated check).
- [ ] Each catalog site's lat/lon maps to the correct DEM cell (spot-checked against Moon Trek or Quickmap for 3 sites).
- [ ] Data README complete; ≥ 1 NASA source in use (DAT-10).
- [ ] **P:** capture a hillshade render of the south-pole AOI with the catalog sites marked (title/problem slide visual).

---

### M2 — Single-site geometry vertical slice (Tracks D + E)

**Goal.** For any catalog site and time, correct Sun/Earth position and visibility against real terrain. **This is the correctness foundation for everything after it.**

**Requirements:** EPH-05–06, HOR-01 (catalog sites), HOR-02–04, VIS-01–04, ACC-01.

**Scope**
- Site az/el computation from the ephemeris.
- Horizon masks for the catalog sites (high azimuth resolution).
- Sunlit state, visible solar fraction, Earth-in-view state, rise and set times.

**Exit criteria**
- [ ] **Validation:** az/el within **0.1°** of direct Horizons `coord@301` queries for ≥ 3 sites × ≥ 3 dates (EPH-05).
- [ ] Horizon mask for ≥ 1 site cross-checked against an independent profile (HOR-06), with any difference documented.
- [ ] A script prints a 30-day sunlit/comms timeline for Mons Mouton, with next sunset/Earthset times.
- [ ] Unit tests for the geometry functions pass.
- [ ] **P:** save the **validation plot** (our elevation vs. Horizons over time, plus the error) for the "Why trust it" slide (PRS-07).

---

### M3 — Single-site mission evaluation + engine operations v1 (Track E)

**Goal.** For the catalog sites, the full mission evaluation works: power, comms, terrain safety, constraints, score and ranking. All of it is exposed as engine operations.

**Requirements:** MSN-01–04, MSN-06, PWR-01–03, PWR-06, COM-01–02, COM-04, TER-04–07, EVL-01–08, ENG-01–03 (site-level operations: list_sites, get_profile_schema, validate_profile, evaluate_site, get_site_timeseries).

**Exit criteria**
- [ ] `evaluate_site` returns metrics, constraint pass/fail with margins, score and component breakdown for all 9 catalog sites under the default profile.
- [ ] Hand-calculated reference case (one site, short window) matches engine output for power, energy, darkness and comms gap.
- [ ] Changing one profile field (e.g. max darkness) changes pass/fail as expected (scripted test).
- [ ] The same input gives the same output (EVL-08).
- [ ] **A track kick-off:** ENG operation schemas frozen as v1 and shared with the A and U tracks.
- [ ] **P:** capture a table or chart of the 9 Artemis regions ranked under the default mission (early "real numbers" for the story).

---

### M4 — Walking-skeleton UI ★ (Track U)

**Goal.** The first demoable app. Runs in a browser, using the M3 engine.

**Requirements:** SIT-03 (list part), MSN-01–02 (form), SKY-01–05, TML-01–02, USE-01–02, PLAT-01, MAP-01 (basic map with catalog markers only), LVL-01 (Simple + Standard), LVL-03–04, LVL-06–07.

**Why levels this early:** novices are a core audience. Building Simple level into the first UI avoids retrofitting jargon-heavy screens later.

**Exit criteria**
- [ ] From a fresh browser: open the app → pick a catalog site → sky view with horizon, Sun and Earth tracks, and countdowns → timeline scrub updates the sky view. **≤ 3 interactions** to the first evaluation (USE-01).
- [ ] Demo steps 3 and 5 from requirements §12 work for catalog sites.
- [ ] Simple level shows a Good / Marginal / Unusable verdict with ≤ 3 everyday metrics; switching to Standard shows the same verdict with full metrics (LVL-06 test).
- [ ] Runs in Chrome, Firefox and Safari.
- [ ] Tagged `m4`; a demo screen recording saved (insurance).
- [ ] **P:** first hero clip: the Sun skimming the horizon in the sky view while the timeline scrubs (video 4–10 s segment).

---

### M5 — Grid scale & map (Tracks D + E + U)

**Goal.** Move from catalog sites to the **whole AOI**: overlays, red unusable areas, top-N, click-anywhere evaluation.

**Requirements:** HOR-01 (all cells), HOR-05, VIS-05, MAP-02 (sunlit, energy, comms, darkness, slope, viability), MAP-03–07, MAP-09, SIT-03 (click to add), EVL-07 (grid), ENG search_grid, PERF-01–03, PERF-05, DAT-13.

**Exit criteria**
- [ ] Horizon masks generated for the full AOI within the data size budget.
- [ ] All MVP overlays toggle, with legends and units; unusable areas red; top-5 marked.
- [ ] Click any point → metrics → "add as site" works.
- [ ] Grid values at catalog-site locations match M3 single-site results (consistency test).
- [ ] PERF-02 (≤ 1 s single site) and PERF-03 (≤ 10 s grid, 30 days) met on a team laptop; UI never freezes.
- [ ] Demo steps 1–5 from §12 pass end to end. **MVP reached.**
- [ ] **P:** capture map overlays (sunlit %, comms %, viability with red areas) at 1920×1080; draft slides 1–4 using the doc figures (architecture, user spectrum).

---

### M6 — Compare, date sweep & mission guidance (Tracks E + U)

**Requirements:** CMP-01–03, SLP-01–04, ENG compare_sites, date_sweep and get_mission_guidance, TML-03–04, PWR-04–05, COM-03, HEU-01–07, HEU-09.

**Why together:** sensitivity and seasonality reuse the same repeated-evaluation machinery as the date sweep.

**Exit criteria**
- [ ] 2–4 sites side by side with aligned timelines and best-value highlighting.
- [ ] 60-day date sweep heatmap for 5 sites within **[TBD]** s; clicking a cell loads that site and date.
- [ ] Mission guidance for the default profile shows the viable fraction, binding constraint, sensitivity per parameter, best and worst months, and terrain-type comparison, as 3–6 plain-language rules, each linked to a supporting view.
- [ ] Sanity check: relaxing the binding constraint increases the viable fraction; tightening it decreases it (scripted).
- [ ] TBDs #14–15 resolved.
- [ ] Demo step 6 passes.
- [ ] **P:** capture the date-slip heatmap and find the real **before/after story number** for PRS-06 (e.g. a site that flips Good → Unusable after a 2-week slip).

---

### M7 — Thermal & resources (Tracks D + E + U)

**Goal.** Add the temperature environment and resource proximity. **Needed before M8**, because the depot archetype depends on it.

**Requirements:** THM-01–06, RES-01–05, RES-07, DAT-05, DAT-08–09, MAP-02 (temperature, PSR, cold-trap overlays), ENG get_resource_info.

**Exit criteria**
- [ ] Temperature min/max/mean per site over a mission window, labeled "surface".
- [ ] PSR and cold-trap overlays shown; distance-to-resource reported per site and usable as a constraint and as a score weight.
- [ ] Spot-check: a known PSR crater (e.g. Shackleton or Haworth interior) shows as PSR and cold trap; a known sunlit ridge does not.

---

### M8 — AI Mission Agent (Track A, with E + U)

Built in **three sub-milestones**, so the feature always works even if the LLM part slips.

#### M8a — Archetypes + search, no LLM

**Requirements:** §7.18.4 archetypes, AGT-05, AGT-07–11, AGT-20, ENG search_grid with min separation, AUI-05–06, AUI-10 (form mode).

**Exit criteria**
- [ ] Pick "Refueling depot" + "2028" in a form → mission guidance + 3–5 spatially distinct candidates with landing windows, metrics and template rationale (HEU-08); cards highlight on the map and open the sky view and compare.
- [ ] The no-solution case gives binding constraints and suggested relaxations (AGT-11).
- [ ] TBDs #11–12 resolved.

#### M8b — LLM agent core

**Requirements:** AGT-01–04, AGT-06, AGT-12, AGT-14–17, AGT-21–23, AUI-01–04, AUI-07–09, AUI-11–12, LVL-02, LVL-09.

**Exit criteria**
- [ ] The depot prompt (requirements §12 step 7) runs end to end: clarifying chips → editable inferred profile with reasons and badges → candidate cards → hand-off to views.
- [ ] **Grounding check passes:** an automated validator confirms every coordinate, date and metric in the agent output matches an engine result ID (AGT-14). A deliberately corrupted output is rejected.
- [ ] The same prompt at Simple vs. Standard level gives different wording but identical candidates and numbers (LVL-09).
- [ ] LLM key not present in client bundle (AGT-22).
- [ ] Turning the LLM off falls back to M8a form mode automatically.
- [ ] TBD #10 resolved.

#### M8c — Agent quality

**Requirements:** AGT-13, AGT-18–19.

**Exit criteria**
- [ ] Evaluation set of ≥ 10 prompts (every archetype, plus out-of-range time frame, an impossible request, an off-topic request) passes AGT-18: ≥ 80% profile accuracy, 100% hard-constraint compliance, 0 ungrounded values.
- [ ] First results ≤ 30 s (AGT-19).
- [ ] Agent demo recorded as a backup (C-5).
- [ ] **P:** capture the depot agent flow (goal → profile card → candidates on the map) for video 10–20 s and slide 5.

---

### M9 — Explainer, Expert level & user testing (Track U)

**Requirements:** EDU-01–03, EPH-07, LVL-05, LVL-08, USE-03–06, ACC-02–04, MAP-08 (C), EXP-01–02 (C), SIT-02, SIT-04 (C).

**Exit criteria**
- [ ] Explainer topics from EDU-02 present; guided two-site demo works.
- [ ] Assumptions & Limitations page and in-app NASA data credits present.
- [ ] Sunlit % for ≥ 1 site compared against published LOLA illumination results, with the difference documented (ACC-02).
- [ ] Expert level exposes all profile fields, weights, raw time series and export.
- [ ] **User tests:** novice test (USE-05, ≥ 3 people) and concept-designer test (USE-06, ≥ 2 people) run; fixes made for anything that blocked them. Recruit friends or classmates outside the team.
- [ ] Accessibility pass: colorblind-safe scales, red areas also patterned.
- [ ] **P:** demo mode (PRS-03) and presentation mode (PRS-04) working; a short quote or observation from user testing for the Impact slide.

---

### M10 — Hardening, presentation & submission (all tracks, led by P)

Split into two halves so presentation never gets squeezed.

#### M10a — Freeze & harden (first ~40% of M10)

- [ ] **Feature freeze.** Only bug fixes after this point.
- [ ] Full demo scenario (requirements §12) rehearsed twice without errors, on the deployed build.
- [ ] Deployed to static hosting, plus the agent proxy if M8b shipped; demo mode works with the network off.
- [ ] README: setup, data prep, run, architecture summary (reuse the figure), data sources.
- [ ] All "M" requirements verified; `docs/progress.md` final.

#### M10b — Presentation & submission (last ~60% of M10)

- [ ] **30 s video** (PRS-01) cut from milestone clips, following §12A.3. ≤ 30 s; captions on; readable on a phone; NASA datasets named on screen.
- [ ] **7-slide deck** (PRS-01), using the doc figures and the captured screenshots; ≤ ~25 words per slide.
- [ ] Before/after story number verified against the live app (PRS-06).
- [ ] Project page text: problem, solution, NASA data used and how (PRS-02), user spectrum, AI use and its grounding, limitations, links.
- [ ] All links public and tested in a private/incognito window (video, slides, app, repo).
- [ ] **Backup recordings** of every key flow stored (PRS-08).
- [ ] If there's a live pitch: 2-minute talk track rehearsed with the deck and demo mode; one person drives, one talks.
- [ ] Submission complete before the deadline, with a buffer of **[TBD, ≥ 1 hour]**.

## 5. Time allocation

The hackathon length and our available hours are **[TBD]**. As a starting split of total build time:

| Milestone | Share | Notes |
|---|---|---|
| M0 | 5% | Keep the technical design doc short |
| M1 | 10% | Big downloads: start these first |
| M2 | 11% | Don't skip validation |
| M3 | 10% | |
| M4 | 10% | U track has been building components since M1 |
| M5 | 13% | Heaviest: performance tuning |
| M6 | 8% | Includes mission guidance |
| M7 | 6% | |
| M8 | 14% | 8a 4% · 8b 7% · 8c 3% |
| M9 | 5% | Includes user tests, which can be short (~15 min each) |
| M10 | 8% | Never compress this. ~40% hardening, ~60% presentation |

**Example: 48-hour event** (≈ 4 people × ~32 working hours). M0–M3 in hours 0–14. M4 by hour 18. M5 by hour 28. M6, M7 and M8a in parallel, hours 28–36. M8b and M9 by hour 42. M10 from hour 42 on (hardening 42–44, presentation 44–48). Track P starts cutting the video from milestone clips at hour ~36, in parallel. If M5 isn't done by hour 32, drop M6 and M9 and go straight to M8a and then M10.

---

## 6. Risks and mitigations

| Risk | Impact | Mitigation | Milestone |
|---|---|---|---|
| Geometry or frame error (wrong az/el) | All results wrong | Horizons validation gate | M2 |
| Horizon masks too slow or large for the full AOI | No map overlays | Coarser grid or fewer azimuths; smaller AOI; precompute offline | M5 |
| Large DEM downloads slow | Blocks M1 | Start downloads in M0; use 80 m data first, 20 m later | M0/M1 |
| Browser performance | Laggy UI | Web Workers; precomputed aggregates; progressive rendering | M5 |
| LLM hallucinated sites or numbers | Credibility loss in front of judges | Engine grounding validator; archetype fallback | M8b |
| LLM API down or rate-limited during judging | Agent demo fails | Form mode (M8a) + recorded backup | M8 |
| Novices confused by jargon | Misses a core audience | Simple level from M4; novice test in M9 | M4/M9 |
| Presentation squeezed by last-minute features | Strong work, weak score on Presentation | Feature freeze at M10a; assets captured every milestone; P owner from M0 | All/M10 |
| Scope creep into "C" items | MVP not finished | Cut line; no C work before M5 passes | All |
| Integration surprises between tracks | Late breakage | ENG schemas frozen at M3; consistency tests in M5 | M3/M5 |
