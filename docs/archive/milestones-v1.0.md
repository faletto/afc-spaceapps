# Lunar Landing Site Navigator — Development Milestones

*NASA Space Apps Challenge 2026 · Team afc-spaceapps · v1.0 · 14 Nov 2026*

*Builds **H1** of `docs/requirements.md` v1.0 (the Zillow-style parcel explorer). H2 and H3 are roadmap items, not milestones. Earlier version: `docs/archive/milestones-v0.2.md`.*

![Build plan](img/roadmap.png)

---

## 1. How we build

We build **module by module, in vertical slices**: one thing working end to end, then widen.

- **Every milestone ends in something that runs and has been checked.** A failure costs one module, not the project.
- **Correctness comes first.** Sun/Earth geometry is validated against JPL Horizons at M2, before anything is scaled to a whole map.
- **We have a demo from M4 onward.** Later milestones make it better; none of them create it.
- **Tracks work in parallel.** Once the engine operations are fixed (M3), the interface, AI and presentation work proceed independently, using mock data until the real data is ready.

**One-shot generation is allowed.** Whether a module is written by hand or generated in one go, it gets the module's requirement IDs, its interfaces and its exit criteria as the spec. It is accepted only if it passes the **same exit criteria**. If a one-shot attempt fails, fall back to the module-by-module path from the last passed milestone.

### 1.1 Rules

- Exit criteria are pass/fail. A milestone is done only when all of them pass.
- Each milestone ends with a git tag (`m0`, `m1`, …) and a three-line note in `docs/progress.md`: what works, what was validated, known issues.
- **Capture presentation assets at every milestone.** Save 1–3 clean screenshots or a clip of 10 seconds or less to `docs/presentation/mN/` (requirement PRS-08).
- **Cut line:** if time runs short, stop at the last passed milestone and polish it. Don't half-build the next one.
- **Nothing from H2 or H3 gets built during the hackathon.** H2/H3 ideas go into `docs/roadmap-ideas.md` instead.

---

## 2. Tracks

| Track | Covers | Main requirement areas |
|---|---|---|
| **D — Data** | Fetch and prepare the NASA data offline | EPH, TER, HOR, ICE/THM data, DAT |
| **E — Engine** | Metrics, parcels, scoring, scenarios, operations | VIS, PWR, COM, ICE, THM, PCL, SCR, USE, SCN, ENG |
| **U — Interface** | The explorer | EXP, TRU |
| **A — AI** | "Describe what you want" | AI |
| **P — Presentation** | Story, assets, demo mode, video, slides | PRS, §14 |

For a team of four: one person each on D/E/U, and A + P shared by the fourth. P has a **named owner from M0**.

---

## 3. Overview

| # | Milestone | What exists at the end | Pri | Depends on |
|---|---|---|---|---|
| **M0** | Foundations & decisions | Repo, open questions resolved, technical design doc, story draft | M | — |
| **M1** | Data foundation | NASA data fetched, documented, loadable | M | M0 |
| **M2** | Geometry, validated | Correct Sun/Earth positions + terrain horizons at chosen locations, checked against Horizons | M | M1 |
| **M3** | Metrics & scoring | Sunlight, nights, contact, ice, temperature, verdicts and scores for chosen locations; engine operations v1 | M | M2 |
| **M4** | Parcel page ★ | First demo: open a parcel for a few named regions and see its full property report | M | M3 |
| **M5** | Parcel map & listings (MVP) | Whole parcel grid; search → listings; layers; No-go areas | M | M3, M4 |
| **M6** | Scenarios | Go later (+ best times), relay upgrade | M/S | M5 |
| **M7** | Describe what you want | AI text box with grounding and a form fallback | S | M5 |
| **M8** | Trust & polish | Data and assumptions pages, filters, novice test, demo and presentation modes | M/S | M5 |
| **M9** | Hardening & submission | Feature freeze, rehearsals, video, slides, project page, submission | M | everything completed |

★ = we have a demo from here on.

**MVP line: M0–M5 + M6 (go later) + M9.** That alone meets the brief and tells the core story.

### 3.1 Dependencies and parallel work

```
M0 ─▶ M1 ─▶ M2 ─▶ M3 ─▶ M4 ─▶ M5 ─┬─▶ M6 ──┐
                         │          ├─▶ M7 ──┼─▶ M9
                         │          └─▶ M8 ──┘
  U: map shell, parcel page layout, sky-view component on mock data from M1
  A: prompt and interpretation design against M3 schemas
  P: story and assets throughout
```

---

## 4. Milestone details

### M0 — Foundations & decisions

**Covers:** requirements §16 open questions #1–9 and #11.

**Exit criteria:**
- [ ] Product name and tagline chosen.
- [ ] Area of interest, analysis-cell resolution and parcel size chosen.
- [ ] Use-type gates and targets, verdict threshold, combining method and tie rules chosen.
- [ ] All of the above recorded in `requirements.md` as v1.1.
- [ ] Technical design doc written and reviewed: architecture, languages, data formats, engine operation signatures, coordinate conventions.
- [ ] Repo skeleton (`data-prep/ engine/ app/ ai/ docs/`), with a test command that runs.
- [ ] **P:** story agreed (requirements §14.5). `docs/presentation/` created.
- [ ] **D:** large downloads started.

### M1 — Data foundation (D)

**Covers:** EPH-01, TER-01, DAT-01 to DAT-06, DAT-10 to DAT-12.

**Exit criteria:**
- [ ] Horizons ephemeris for 2026–2030 at 1-hour steps stored, with no gaps (automated check).
- [ ] LOLA elevation and slope (plus error) cropped to the area of interest.
- [ ] Diviner polar temperatures stored.
- [ ] Named regions and coordinates stored, with sources.
- [ ] Scripts rerun from scratch reproduce all of the data.
- [ ] Data README complete.
- [ ] Spot check: three named regions land on the right terrain, compared with Moon Trek or Quickmap.
- [ ] **P:** a hillshade render of the south pole with region labels (title-slide visual).

### M2 — Geometry, validated (D + E)

**Covers:** EPH-02, HOR-01 (for chosen locations), VIS-01, VIS-02.

**Exit criteria:**
- [ ] **Validation passes:** Sun and Earth elevation within 0.1° of Horizons at three or more locations on three or more dates.
- [ ] Terrain horizon for one location cross-checked against an independent profile (Moon Trek or Quickmap), with any difference written down.
- [ ] A script prints a 30-day sunlit / Earth-contact timeline for one named region, including the next sunset and Earthset.
- [ ] Geometry unit tests pass.
- [ ] **P:** validation plot saved: our elevation vs. Horizons over time, plus the error (for the "Why trust it" slide).

### M3 — Metrics & scoring (E)

**Covers:** PWR-01, COM-01, ICE-01, THM-01, TER-02, SCR-01 to SCR-05, SCR-08, SCR-09, USE-01, USE-03, ENG-01 to ENG-03 (location-level operations).

**Exit criteria:**
- [ ] For each named region's chosen location, under each of the four use types, the engine returns metrics, gate pass/fail with margins, score and verdict.
- [ ] One hand-calculated reference case matches the engine (sunlight %, longest night, longest silence).
- [ ] Sanity tests (SCR-09) run automatically and pass.
- [ ] Engine operation schemas frozen at v1 and shared with the U and A tracks.
- [ ] **P:** a table of the named regions × use types with verdicts (first real numbers for the story).

### M4 — Parcel page ★ (U + E)

**Covers:** PCL-02 to PCL-07 (for parcels in the named regions), EXP-06, EXP-07, EXP-08, EXP-12, TRU-05.

**Exit criteria:**
- [ ] In a browser, choose a named region → its parcel page shows:
  - score, verdict and why line;
  - best-for tags and fact sheet;
  - sky view with countdowns and animation;
  - timeline linked to the sky view;
  - through-the-year chart;
  - best landing window, main risk, and the "not assessed" list.
- [ ] Runs in Chrome, Firefox and Safari.
- [ ] Tagged `m4`; screen recording saved.
- [ ] **P:** hero clip of the Sun skimming the horizon while the timeline scrubs (video 4–10 s).

### M5 — Parcel map & listings: MVP (D + E + U)

**Covers:** HOR-01 (all cells), PCL-01, PCL-08, PCL-09, EXP-01 to EXP-05, EXP-09, EXP-13, NFR-03, NFR-05, DAT-13.

**Exit criteria:**
- [ ] Terrain horizons and metrics computed for every analysis cell, within the data size budget.
- [ ] Full parcel grid colored by Site Score; hovering shows quick facts, clicking opens the parcel page.
- [ ] Search by use type + time frame (+ what matters most) recolors the map and shows ranked listings.
- [ ] No-go areas are red **and** hatched.
- [ ] Parcel values match their cells (consistency test).
- [ ] Performance targets met (NFR-03).
- [ ] A new user reaches a parcel page in three interactions or fewer.
- [ ] Demo steps 1–4 (requirements §13) pass. **MVP reached.**
- [ ] **P:** map captures at 1920×1080 (balanced score, lodge search, depot search). Draft slides 1–4.

### M6 — Scenarios (E + U)

**Covers:** SCN-01 (M), SCN-02 (S), SCN-03 and SCN-04 (S), SCR-06 and SCR-07 (ties, S).

**Exit criteria:**
- [ ] "Go later" presets and slider update the map and listings, with rank and verdict changes highlighted.
- [ ] *(S)* Best-times strip on the parcel page.
- [ ] *(S)* Relay toggle updates the map and shows the change in Good parcels, reported neutrally.
- [ ] *(S)* Tied scores labeled; tie-break order applied.
- [ ] Demo steps 5–6 pass.
- [ ] **P:** find the real **before/after number** (PRS-05). Capture the go-later and relay clips (video 18–25 s).

### M7 — Describe what you want (A + U)

**Covers:** AI-01 to AI-06.

**Exit criteria:**
- [ ] "A fuel depot near ice in 2028" → editable interpretation chips → depot listings near cold traps.
- [ ] Grounding validator passes, and a deliberately corrupted output is rejected.
- [ ] Out-of-scope requests (e.g. "how much does a parcel cost?") get an honest redirect.
- [ ] With the AI disabled, the search form works on its own.
- [ ] The AI key is not in the client.
- [ ] A test set of 8 or more requests passes, with interpretations judged correct by the team.
- [ ] **P:** capture "Same Moon, different listings" (lodge vs. depot, side by side) for slides 3–4.

### M8 — Trust & polish (U + P)

**Covers:** TRU-01 to TRU-04, EXP-10 (S), EXP-11 (C), PRS-02, PRS-03, PRS-04, NFR-07.

**Exit criteria:**
- [ ] About the data, Assumptions & limits, and the validation view are in the app.
- [ ] Demo mode loads every preset scenario offline.
- [ ] Presentation mode works.
- [ ] Novice test run with three or more people from outside the team; anything that blocked them is fixed.
- [ ] *(S)* Filters. *(C)* Compare two parcels.
- [ ] **P:** one observation or quote from the novice test for the Impact slide.

### M9 — Hardening & submission (all, led by P)

**M9a — Freeze & harden (about 40% of M9):**
- [ ] Feature freeze: bug fixes only.
- [ ] Demo flow (requirements §13) rehearsed twice without errors on the deployed build.
- [ ] Demo mode verified with the network off.
- [ ] README complete: setup, data prep, run, architecture figure, data sources.
- [ ] All H1 **M** requirements verified.

**M9b — Presentation & submission (about 60% of M9):**
- [ ] 30-second video cut from the milestone clips, following §14.5. Captions on, readable on a phone, NASA datasets named on screen.
- [ ] 7-slide deck using the doc figures and the captures.
- [ ] Before/after number re-checked against the live app.
- [ ] Project page written: problem, idea, NASA data and how it's used, listings-not-deeds, limits, roadmap, links.
- [ ] All links tested in a private browser window.
- [ ] Backup recordings stored.
- [ ] If there's a live pitch: a 2-minute talk track rehearsed, with one person driving and one talking.
- [ ] Submitted at least **[TBD, e.g. 1 hour]** before the deadline.

---

## 5. Time allocation

The hackathon length is **[TBD]**. As a share of build time:

| M0 | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | M9 |
|---|---|---|---|---|---|---|---|---|---|
| 5% | 10% | 11% | 10% | 10% | 16% | 10% | 9% | 8% | 11% |

**Example: a 48-hour event**

| Hours | Milestones |
|---|---|
| 0–14 | M0–M3 |
| by 18 | M4 |
| by 28 | M5 |
| 28–38 | M6, M7 and M8 in parallel |
| 38–48 | M9 (P starts cutting the video around hour 34) |

If M5 isn't done by hour 32: drop M7 and M8's optional items, and keep M6 "go later" plus M9.

---

## 6. Risks

| Risk | Mitigation | Where |
|---|---|---|
| Wrong geometry or reference frame | Horizons validation gate | M2 |
| Terrain horizons too slow or too large for the full grid | Coarser cells or fewer azimuths; smaller area; precompute offline | M5 |
| Slow downloads | Start in M0; use 80 m data first | M0–M1 |
| Parcel aggregation hides problems inside a parcel | Show buildable area and best spot; consistency test | M4–M5 |
| Scores feel arbitrary | Fixed normalization; sanity tests; why lines; tie labels | M3–M6 |
| "Zillow" read as owning or selling the Moon | Listings-not-deeds wording, no prices, assumptions page | M4, M8 |
| AI makes up places or numbers | Grounding validator; form fallback | M7 |
| AI or network down during judging | Demo mode plus recordings | M8–M9 |
| Presentation squeezed at the end | Feature freeze in M9a; assets captured every milestone; P owner from M0 | All |
| Scope creep into H2/H3 | Ideas go to `roadmap-ideas.md`, not into code | All |
