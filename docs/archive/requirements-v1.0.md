# Lunar Landing Site Navigator — Requirements & System Definition

*NASA Space Apps Challenge 2026 · Team afc-spaceapps*

*Version 1.0 (re-baselined) · 14 Nov 2026*

*v1.0 rescopes the product as a **Zillow-style explorer for the lunar south pole**, built for **anyone**. The region is divided into a **parcel grid**, and every parcel gets a property evaluation. Requirements are tagged by horizon (H1 hackathon / H2 next / H3 vision). Earlier versions are archived in `docs/archive/`, and requirement IDs are re-baselined from this version.*

---

## At a glance

> **Browse the Moon like you browse homes.** Pick what you want to put there (a first lander, a lodge, a solar farm, a fuel depot) and when. The app shows a map of the lunar south pole divided into **parcels**. Each parcel has a simple **property evaluation**: how much sunlight it gets, how long its nights last, how often you can talk to Earth, whether there's flat ground to land and build on, and how far it is to ice. Behind the simple view is real NASA data and real geometry: the Sun and Earth tracked against the actual terrain horizon.

| | Summary |
|---|---|
| **Problem** | At the Moon's south pole, a few kilometers or a few days can turn 80% sunlight into 20%, and constant Earth contact into silence. NASA's tools hold the answers but are built for specialists. |
| **Solution** | A Zillow-like map of parcels, each with a fact sheet, a score, and "best for" tags, plus listings for what you want to build and when, and one-click "what if" scenarios. |
| **Who it's for** | **Anyone**: students, teachers, space fans, founders, policy staff, journalists. No lunar expertise needed. |
| **Built on** | NASA JPL Horizons (Sun/Earth positions), LRO LOLA (terrain), LRO Diviner (temperatures, cold traps), Moon Trek (basemap). |
| **What makes it different** | Terrain-aware horizons, not a smooth sphere. Evaluation over a whole time frame, not one moment. A familiar real-estate-style interface on top of rigorous analysis. "What if we launch later?" and "what if a relay satellite existed?" scenarios. |

![How people use it](img/personas.png)

---

## 0. Document control

| Item | Value |
|---|---|
| Purpose | Define **what** the product must do and **how well**. This is the baseline for the technical design document. |
| Not in this document | Algorithms, code structure, libraries, file formats. These belong in the technical design doc. |
| Inputs | Challenge brief and Resources tab; team notes; `docs/plan-review.md`; team decisions from 14 Nov (Zillow framing, novice users, parcel grid, horizons) |
| Status | Draft for team review. Open items are marked **[TBD]** and collected in §16. |

### 0.1 Conventions

- **IDs:** `<AREA>-<NN>`. They are re-baselined in v1.0 and never reused after this point.
- **Wording:** "shall" = required; "should" = desired; "may" = optional.
- **Horizon:**
  - **H1** = build and demo at the hackathon.
  - **H2** = next product version (roadmap).
  - **H3** = long-term vision.
- **Priority (H1 only):**
  - **M** = Must (needed for the demo)
  - **S** = Should
  - **C** = Could
- **Verification:**
  - **T** = Test
  - **D** = Demonstration
  - **I** = Inspection
  - **A** = Analysis against a reference

---

## 1. Purpose and positioning

### 1.1 Purpose

Give **anyone** a fast, intuitive way to answer:

> *"Where near the Moon's south pole would it make sense to land, live or build, and when?"*

The challenge asks for a tool that lets people compare landing sites and dates quickly, by showing the Sun and Earth relative to the horizon so they can judge power and direct-to-Earth communication. This product answers that through a familiar metaphor, real estate. The south pole becomes a map of parcels with fact sheets, scores, listings and "what if" scenarios.

### 1.2 Positioning: "Like Zillow, for the Moon"

| Zillow | This product |
|---|---|
| Neighborhoods | Named regions (e.g. NASA's Artemis III candidate regions) |
| Every home, for sale or not | Every **parcel** on the grid |
| Home facts (beds, baths, sq ft) | **Parcel facts**: sunlight %, longest night, Earth contact %, buildable area, distance to ice, temperature range |
| Zestimate | **Site Score** (0–100) with a plain-language "why" |
| Property type (house, condo, land) | **Use type**: first lander, lodge / home base, solar farm, propellant depot |
| Search + filters | Pick a use + time frame (+ optional "what matters most") |
| Listings | The best parcels for your use and time frame |
| Price history chart | **Sunlight and Earth contact through the year** chart |
| Map with colored pins | Map with parcels colored Good / Marginal / No-go |
| Neighborhood improvements | **Upgrades** (e.g. "add a relay satellite") and their effect on the map |

### 1.3 Listings, not deeds

- The product evaluates **suitability**. It shall **not** present parcels as property for sale or ownership. There are no prices, no "buy", and no ownership claims (see §12).
- The product is a **screening and learning tool**, not certified mission analysis, and says so in the interface.
- "Zillow" is used as a **comparison** in pitches, not as product branding. The product name is **[TBD]**.

---

## 2. Scope by horizon

### 2.1 H1 — Hackathon build (in scope)

- The south polar region **80°S–90°S**. The parcel grid covers an area of interest of **[TBD: 88°S–90°S or larger]**.
- Time frames within **2026–2030**, analyzed at 1-hour steps.
- The **parcel grid** with a property evaluation for every parcel.
- **Four use types:** First lander · Lodge / home base · Solar farm · Propellant depot.
- **Search → listings → parcel page** flow, including the sky view and the "through the year" chart.
- **Scenarios:** "What if we go later?" (date shift) and one **upgrade** toggle (relay satellite).
- An **AI "describe what you want"** box (Should), with a form-based fallback.
- **Trust features:** "why" lines, a validation against JPL Horizons, an assumptions page, data credits.
- **Demo and presentation** features.

### 2.2 H2 — Next version (roadmap, not built at the hackathon)

- **Expert mode:** adjustable weights and targets, raw time series, export.
- Side-by-side comparison of 3+ parcels; a one-page shareable brief (PDF); saved favorites and saved searches.
- More use types: in-situ manufacturing, satellite assembly, comms relay station, ice-prospecting rover base, tourist resort.
- **Rover routes** between parcels ("commute"), and a reach score.
- More upgrades: fission surface power, precision landing.
- Experience extras: Earth phase and "best week to visit".
- North pole coverage; finer parcels near top sites.

### 2.3 H3 — Vision

- **Development planning:** place several connected facilities together (landing pad, solar farm, depot, homes, routes) as a lunar "town", and evaluate them as a cluster.
- Speculative infrastructure: mass drivers, large-scale manufacturing, resorts.
- Live data updates as new missions map the Moon; other worlds (e.g. Mars).

### 2.4 Out of scope (all horizons unless revisited)

| Item | Reason |
|---|---|
| Ownership, pricing, transactions | Legal and ethical (§12); not the product's purpose |
| Costs and budgets | No credible data; would undermine credibility |
| Regolith composition / mineral prospecting | Needs other datasets; not part of the brief |
| Launch trajectories, Δv, "effort to get there" | Beyond the brief |
| Boulder-scale hazards | Below elevation-map resolution |
| Crew medical or safety certification | Not a certified tool |

---

## 3. Users

### 3.1 Primary user: anyone

The product is designed for **a regular person browsing, the way anyone browses Zillow**, with no lunar expertise assumed. That includes:

- a student working on a project,
- a teacher preparing a class,
- a space fan curious where a Moon base could go,
- a founder sketching a business idea,
- a policy intern or journalist who needs a quick, defensible answer.

All of them use the **same interface**. There are no separate modes per user type in H1.

### 3.2 Secondary (H2): technical users

Engineers and researchers who want to tune the analysis are served later by **Expert mode** (H2). In H1, their needs are met by validation, transparency and stated assumptions, not by extra controls.

### 3.3 Hackathon judges

Judges see a 30-second video or ≤ 7 slides, the project page, and possibly a short live demo. Everything important must be **visible within seconds** (§14).

### 3.4 Design principles

- **P-1. Zillow-simple.** If a feature needs a tutorial, it's H2.
- **P-2. Plain words first, numbers second.** Verdict and reason first, then facts.
- **P-3. Everyday units.** "Sunlight 78% of the time", "longest night 2 days", "talk to Earth 64% of the time".
- **P-4. Rigor underneath.** Simple presentation never means simplified correctness.
- **P-5. Honest about limits.** Say what is and isn't assessed.

---

## 4. Use cases (H1)

| ID | Use case | Pri |
|---|---|---|
| UC-1 | **Browse the map.** Open the app → a map of parcels colored by Site Score → hover for quick facts. | M |
| UC-2 | **Search for a use and time frame.** Pick a use type (e.g. Lodge) and a time frame (e.g. "2028") → parcels recolor for that use → a list of top listings appears. | M |
| UC-3 | **Open a parcel.** See score, verdict, "best for" tags, fact sheet, the sky view (Sun and Earth against the real horizon), the "through the year" chart, best landing window, and main risk. | M |
| UC-4 | **What if we go later?** Shift the time frame → listings and colors update; changes are highlighted (e.g. "#1 drops to Marginal"). | M |
| UC-5 | **What if there were a relay?** Toggle the upgrade → the map updates; the change in Good area is shown. | S |
| UC-6 | **Describe what you want.** Type e.g. "a small lodge for visitors in 2028" → the app picks the use type, time frame and priorities and shows listings, with its interpretation visible and editable. | S |
| UC-7 | **Custom spot.** Click anywhere → that parcel's page. | M |
| UC-8 | **Compare two parcels.** | C |

---

## 5. Product concept

### 5.1 Parcels

- The area of interest is divided into a **fixed square grid of parcels** in polar stereographic coordinates. Default parcel size is **[TBD, e.g. 1 km × 1 km]**.
- Each parcel is built from many finer **analysis cells** (e.g. 240 m), so parcel facts summarize what's inside it: for example "62% of this parcel is flat enough to build on".
- Each parcel has a stable **parcel ID** (grid reference) and a **display name**: the nearest named feature or region, e.g. "Mons Mouton · Parcel 14-07".
- Within each parcel, the **best spot** is identified: the analysis cell that scores best for the selected use.

### 5.2 Property evaluation (every parcel)

Every parcel always has an evaluation, even without a search, just as every home on Zillow has an estimate:

1. **Fact sheet**

   | Fact | Shown as |
   |---|---|
   | Sunlight | % of time sunlit |
   | Longest night | Longest continuous darkness |
   | Earth contact | % of time Earth is in view |
   | Longest silence | Longest gap without Earth contact |
   | Buildable area | % of parcel within the slope limit |
   | Steepness | Typical and maximum slope |
   | Distance to ice | km to nearest cold trap |
   | Temperature range | Surface min–max |
   | Data confidence | High / Medium / Low |

2. **Site Score (0–100)** under a neutral, **balanced** profile. This is the headline number.
3. **Best-for tags:** a Good / Marginal / No-go verdict for each use type, and the top 1–2 uses (e.g. "Best for: Solar farm, Lodge").
4. **"Why" line:** one sentence on what drives the score (e.g. "Ridge top: long sunlight, but 14 km from ice").
5. **Through the year:** a monthly chart of sunlight and Earth contact, the "price history" equivalent.

The default evaluation period is **[TBD, e.g. calendar year 2028]**. When the user picks a time frame, the evaluation is recomputed for it.

### 5.3 Use types (H1)

Each use type defines hard requirements (**gates**), **targets**, and **default priorities**. Values are starting points **[TBD in M0]**.

| Use type | Plain description | Gates (must pass) | Targets (good enough) | Default priorities | Not assessed (shown to the user) |
|---|---|---|---|---|---|
| **First lander** | A robotic lander for a short stay (≈ 10 days) | Slope at the best spot; longest night ≤ 48 h during the stay | Sunlight ≥ 70%; Earth contact ≥ 50% | Safety → Power → Contact | Boulders, approach path |
| **Lodge / home base** | A small crewed habitat for weeks (incl. visitors) | Slope; longest night ≤ 48 h; longest silence ≤ **[TBD]** h | Sunlight ≥ 80%; Earth contact ≥ 85%; buildable ≥ 30% | Contact → Power → Comfort | Life support, crew safety, landing debris |
| **Solar farm** | Power plant supplying nearby facilities | Slope; buildable ≥ **[TBD]** % | Sunlight ≥ 85%; longest night ≤ 24 h | Power → Buildable area | Transmission, panel degradation |
| **Propellant depot** | Turns ice into fuel; needs both sun and ice | Slope; distance to cold trap ≤ **[TBD, e.g. 10]** km; longest night ≤ 72 h | Sunlight ≥ 70%; ice ≤ 5 km | Ice proximity → Power → Contact | Actual ice content, processing, access route |

### 5.4 Scenarios

- **"What if we go later?"** Shift the time frame by days to months and see what changes.
- **Upgrades:** hypothetical infrastructure that changes the constraints. In H1, one upgrade: **relay satellite**, under which Earth-contact gaps no longer apply. The app shows the change in Good parcels.
- Scenarios are **neutral**: they show cases where an upgrade barely helps as well as where it helps a lot.

---

## 6. System overview

### 6.1 Architecture

![System architecture](img/architecture.png)

*NASA data → offline preparation → analysis engine (cells → parcels → scores) → the explorer interface. The AI box and every view call the same **engine operations**, so there is one source of truth.*

### 6.2 Subsystems

| ID | Subsystem | Responsibility | Horizon / Pri |
|---|---|---|---|
| EPH | Ephemeris | Sun and Earth positions over time (JPL Horizons) | H1 / M |
| TER | Terrain | Elevation, slope, buildable area, data confidence (LOLA) | H1 / M |
| HOR | Horizons | Terrain horizon around each cell | H1 / M |
| VIS | Visibility | Sun/Earth position and visible/blocked per cell and hour | H1 / M |
| PWR | Power | Sunlight %, longest night, energy | H1 / M |
| COM | Contact | Earth contact %, longest silence | H1 / M |
| ICE | Ice proximity | Cold traps (Diviner) and distance to them | H1 / M (needed for depot) |
| THM | Temperature | Surface temperature range (Diviner) | H1 / S |
| PCL | Parcels | Parcel grid; aggregation from cells; fact sheet | H1 / M |
| SCR | Scoring | Gates → targets → score; verdicts; ties; ranking | H1 / M |
| USE | Use types | Definitions of the four H1 use types | H1 / M |
| SCN | Scenarios | Date shift; relay upgrade | H1 / M (shift), S (upgrade) |
| ENG | Engine operations | Shared callable operations for UI and AI | H1 / M |
| EXP | Explorer UI | Map, search, listings, parcel page, sky view, charts | H1 / M |
| AI | Describe-what-you-want | Free text → use type, time frame, priorities → listings | H1 / S |
| TRU | Trust | Why lines, validation, assumptions, credits, disclaimers | H1 / M |
| PRS | Presentation | Demo mode, presentation mode, capture, story | H1 / M–S |
| — | Expert mode, comparison+, brief export, routes, more uses, more upgrades | | H2 |
| — | Clusters / towns, speculative infrastructure, other worlds | | H3 |

---

## 7. Key definitions

| Term | Definition |
|---|---|
| **Analysis cell** | The finest grid unit used for computation. Resolution **[TBD, target ≤ 240 m]**. |
| **Parcel** | A fixed square of the grid (**[TBD, e.g. 1 km]**) made of many analysis cells. The unit users browse. |
| **Best spot** | The analysis cell in a parcel with the best score for the selected use. |
| **Time frame** | The period being evaluated, sampled at 1-hour steps. Default **[TBD]**. |
| **Terrain horizon** | For a location, the elevation angle of the highest terrain in each compass direction, including lunar curvature. |
| **Sunlit** | The visible fraction of the solar disk above the terrain horizon is > **[TBD, default 0.5]**. |
| **Earth contact** | Earth's center is above the terrain horizon by at least the antenna margin (default 5°). |
| **Longest night** | The longest continuous run of non-sunlit hours in the time frame. |
| **Longest silence** | The longest continuous run of hours without Earth contact. |
| **Buildable area** | The share of a parcel's cells within the use type's slope limit. |
| **Cold trap** | Surface whose maximum temperature (Diviner) is < 110 K, where water ice can be stable. |
| **Gate** | A hard requirement; failing it means **No-go**. |
| **Target** | The level at which a metric is "good enough"; beyond it, extra counts very little. |
| **Site Score** | 0–100 suitability for a use (or the balanced default). |
| **Verdict** | **No-go** = fails any gate. **Good** = score ≥ **[TBD, e.g. 70]**. **Marginal** = otherwise. |

---

## 8. Functional requirements (H1)

### 8.1 Engine core

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| EPH-01 | Sun and Earth positions relative to the Moon shall come from **JPL Horizons**, precomputed for 2026–2030 at 1-hour steps and bundled. No live calls at runtime. | M | I |
| EPH-02 | Sun and Earth azimuth/elevation derived for any location shall match direct Horizons topocentric queries within **0.1°** (≥ 3 locations × ≥ 3 dates). Earth parallax included. | M | A |
| TER-01 | Terrain shall come from **LRO LOLA south-polar elevation and slope products** (NASA GSFC PGDA). | M | I |
| TER-02 | The system shall provide slope, slope uncertainty and a data-confidence class per analysis cell. | M | T |
| HOR-01 | A terrain horizon (elevation vs. azimuth, ≤ 2° steps) shall be precomputed for every analysis cell, including lunar curvature and terrain out to **[TBD, ≥ 50 km]**. | M | T |
| VIS-01 | For any cell and hour, the system shall determine the Sun and Earth azimuth/elevation, visible solar fraction, sunlit state and Earth-contact state. | M | T |
| VIS-02 | For any cell and time, the system shall compute the next sunset/sunrise and Earthset/Earthrise. | M | T |
| PWR-01 | Per cell and time frame: sunlight %, longest night, and energy for a vertical, Sun-tracking reference panel. | M | T |
| COM-01 | Per cell and time frame: Earth contact %, longest silence, and number of contact windows. | M | T |
| ICE-01 | The system shall derive a **cold-trap map** from **LRO Diviner** (max temperature < 110 K) and compute each cell's distance to the nearest cold trap. | M | T |
| ICE-02 | The UI shall say that cold traps indicate *possible* ice, not confirmed ice. | M | I |
| THM-01 | Per cell: surface temperature range for the time frame, from Diviner. | S | T |

### 8.2 PCL — Parcels and property evaluation

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| PCL-01 | The area of interest shall be divided into a fixed square **parcel grid** (§5.1) with stable IDs and display names. | M | I |
| PCL-02 | Every parcel shall have a **fact sheet** (§5.2) aggregated from its analysis cells, with documented aggregation rules (e.g. buildable area = share of passing cells; sunlight = value at the best spot). | M | T |
| PCL-03 | Every parcel shall have a **Site Score** under the balanced default profile, plus a score per use type. | M | T |
| PCL-04 | Every parcel shall have **best-for tags** (a verdict per use type; top 1–2 uses shown). | M | T |
| PCL-05 | Every parcel shall have a one-sentence **"why" line** generated from its facts and score drivers. | M | D |
| PCL-06 | Every parcel shall have a **through-the-year** monthly series of sunlight % and Earth contact % for the evaluation year. | S | D |
| PCL-07 | Each parcel shall identify its **best spot** for the selected use. | M | T |
| PCL-08 | Parcels shall be grouped into **named regions** (at least NASA's nine Artemis III candidate regions) for labels and browsing. | S | I |
| PCL-09 | Parcel values shall be consistent with the underlying cell values (automated test). | M | T |

### 8.3 SCR — Scoring, verdicts and ranking

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| SCR-01 | Scoring shall use three layers: **gates** (fail = No-go) → **targets** (each metric mapped to 0–1, reaching ~1 at its target with diminishing returns beyond) → a **combined score** over the metrics that pass the gates. | M | T |
| SCR-02 | Metric-to-0–1 mapping shall use **fixed reference ranges** per metric, not ranges relative to the sites shown, so a score means the same thing everywhere and at every date. | M | I |
| SCR-03 | The combination shall penalize weak links: use a **weighted geometric mean** (or a weighted sum with a penalty below a floor) **[TBD in M0]**, so excellence in one metric can't hide failure in another. | M | T |
| SCR-04 | Safety-related terrain criteria shall be gates (plus a margin used for tie-breaking), not tradeable weights. | M | I |
| SCR-05 | Priorities shall come from the use type's defaults, optionally adjusted by a single **"what matters most"** choice: *Power · Earth contact · Safe ground · Balanced*. | M | D |
| SCR-06 | Scores within **±[TBD, e.g. 2]** points shall be treated as **tied** and shown as such. | S | T |
| SCR-07 | Ties shall be broken in this order: (1) **robustness to date shifts** (score change over ±**[TBD]** days); (2) smallest margin to any gate (larger wins); (3) data confidence; (4) parcel ID. | S | T |
| SCR-08 | Ranking and scores shall be deterministic. | M | T |
| SCR-09 | **Sanity tests** shall run automatically: permanently shadowed crater interiors are No-go for solar use; known well-lit ridges score high on sunlight; the Artemis III regions are not all No-go for the First-lander use. | M | T |

### 8.4 USE — Use types

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| USE-01 | The system shall provide the four H1 use types (§5.3), each with gates, targets, default priorities and a **"not assessed"** list. | M | I |
| USE-02 | The parcel page and listings shall show the use type's "not assessed" items. | M | D |
| USE-03 | Use-type definitions shall live in one editable configuration, so H2 can add types without code changes. | S | I |

### 8.5 SCN — Scenarios

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| SCN-01 | **What if we go later?** The user shall shift the time frame (slider or presets: +2 weeks, +1 month, +3 months, +6 months). The map and listings update, and changes in rank or verdict are highlighted. | M | D |
| SCN-02 | The system should show a compact **"best times"** strip for a parcel: its score for each candidate start date over the next **[TBD, e.g. 90]** days. | S | D |
| SCN-03 | **Relay upgrade:** a toggle under which Earth-contact gates and penalties are lifted. The map updates and shows the change in the number or area of Good parcels. | S | D |
| SCN-04 | Scenario results shall be shown neutrally, including when an upgrade changes little. | M (if SCN-03 built) | I |

### 8.6 EXP — Explorer interface

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| EXP-01 | **Home:** a full-screen south-pole map with the parcel grid colored by Site Score, plus a search bar: *What do you want to put here?* (use type) · *When?* (time frame) · optional *What matters most?* | M | D |
| EXP-02 | **Map + list split view:** after a search, parcels recolor (Good / Marginal / No-go for that use) and a ranked **listings** panel shows the top **[TBD, e.g. 10]** parcels. | M | D |
| EXP-03 | **Listing card:** parcel name, verdict badge, score, the three most relevant facts for the use, best landing window, and a thumbnail (hillshade). Hovering a card highlights the parcel. | M | D |
| EXP-04 | **No-go areas** shall be clearly marked (red **and** hatched, so not by color alone). | M | D |
| EXP-05 | **Hover** on any parcel shows a quick-facts tooltip; **click** opens the parcel page. | M | D |
| EXP-06 | **Parcel page:** score and verdict; why line; best-for tags; fact sheet; **sky view**; timeline; through-the-year chart; best landing window; main risk; "not assessed" list; data confidence. | M | D |
| EXP-07 | **Sky view:** the terrain horizon around the best spot, with the Sun's and Earth's paths over the time frame. Blocked segments look different. Countdowns to the next sunset and Earthset. Animated playback. | M | D |
| EXP-08 | **Timeline:** sunlit / dark and contact / no contact bars over the time frame, scrubbable and linked to the sky view. | M | D |
| EXP-09 | **Map layers** (toggle): Site Score, sunlight, longest night, Earth contact, buildable area, distance to ice, named regions. | M | D |
| EXP-10 | **Filters** (should): minimum sunlight, maximum night, maximum distance to ice, minimum buildable area. | S | D |
| EXP-11 | **Compare two parcels** side by side. | C | D |
| EXP-12 | All numbers in everyday units with plain-language tooltips; dates in UTC with readable formatting. | M | I |
| EXP-13 | A first-time user shall reach a parcel page in **≤ 3 interactions**. | M | D |

### 8.7 AI — "Describe what you want"

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| AI-01 | A text box shall accept a plain-language request (e.g. "a small lodge for visitors sometime in 2028"). | S | D |
| AI-02 | The AI shall map it to a **use type, time frame and "what matters most"** choice, show this interpretation as editable chips, and run the normal search. | S | D |
| AI-03 | The AI may ask **one** clarifying question if the request is ambiguous. | S | D |
| AI-04 | **Grounding:** every parcel, number and date the AI shows shall come from engine results. Output is validated before display. | M (if AI built) | T |
| AI-05 | Requests outside scope (unsupported use types, ownership/pricing, non-lunar) shall get a short, honest reply plus the closest supported option. | S | D |
| AI-06 | The search form is the fallback: the product shall work fully with the AI unavailable. LLM credentials never reach the client. | M | D |

### 8.8 TRU — Trust and transparency

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| TRU-01 | An **About the data** page shall list each NASA source, what it's used for, and its resolution. Credits shall be visible in the app. | M | I |
| TRU-02 | An **Assumptions & limits** page shall list the simplifications, "not assessed" items, and the **listings-not-deeds** statement. | M | I |
| TRU-03 | A **validation** result (our Sun/Earth elevations vs. JPL Horizons) shall be shown in the app or docs, and in the presentation. | M | D |
| TRU-04 | Every score shall be explainable on demand: which gates passed, which metrics contributed, and how much. | S | D |
| TRU-05 | A short disclaimer shall be visible: "Screening and learning tool — not certified mission analysis." | M | I |

### 8.9 ENG — Engine operations

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| ENG-01 | The engine shall expose operations used by both the UI and the AI. At least: **get_parcel_grid**, **get_parcel** (facts, scores, tags, why, best spot), **search** (use type, time frame, priority → ranked listings and per-parcel verdicts), **get_timeseries**, **shift_time_frame**, **apply_upgrade**. | M | T |
| ENG-02 | Operations shall take and return structured, schema-defined data with units, and return result IDs for AI grounding. | M | T |
| ENG-03 | Invalid inputs return validation errors, never silent defaults. | M | T |

---

## 9. Data requirements

| ID | Dataset | Source (NASA) | Used for | Pri |
|---|---|---|---|---|
| DAT-01 | Sun/Earth ephemeris 2026–2030, 1 h | JPL Horizons | EPH, VIS | M |
| DAT-02 | South-polar elevation (near and far field) | LRO LOLA via GSFC PGDA | TER, HOR | M |
| DAT-03 | Slope and slope error | LRO LOLA via GSFC PGDA | TER, PCL | M |
| DAT-04 | Polar surface temperatures | LRO Diviner (PDS) | ICE, THM | M |
| DAT-05 | Basemap / hillshade | Moon Trek / LOLA hillshade | EXP | M |
| DAT-06 | Region names and coordinates | NASA Artemis III announcement; other cited sources | PCL-08 | S |

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| DAT-10 | At least one NASA data source shall be used. This plan uses four. | M | I |
| DAT-11 | A data README shall document each source's URL, version, resolution and license, plus how to reproduce the derived products. | M | I |
| DAT-12 | All data shall share one lunar reference frame and radius; any differences shall be documented. | M | A |
| DAT-13 | Bundled data should be ≤ **[TBD, e.g. 200 MB]**, lazy-loaded where possible. | S | I |

---

## 10. Non-functional requirements

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| NFR-01 | Runs in current Chrome, Firefox and Safari with no install; usable on a tablet. | M | D |
| NFR-02 | Static hosting (e.g. GitHub Pages). The only exception is a minimal proxy for the AI (AI-06). | S | I |
| NFR-03 | First interactive map ≤ **10 s**; parcel page ≤ **1 s**; a new search or time shift ≤ **5 s**, with progress shown and the UI never frozen. | M | T |
| NFR-04 | Sky-view animation and timeline scrubbing at ≥ **20 fps**. | S | T |
| NFR-05 | Colorblind-safe palettes; verdicts never conveyed by color alone. | M | I |
| NFR-06 | The data-prep pipeline is reproducible from documented scripts; core calculations have automated tests. | M | I |
| NFR-07 | **Novice test:** ≥ 3 people with no lunar background, given "find a good place for a small lodge in 2028", reach a parcel page and explain in one sentence why it's good or bad, without help. | S | D |

---

## 11. Interfaces (logical)

| From → To | Information |
|---|---|
| EPH, HOR → VIS | Hourly Sun/Earth directions; terrain horizons |
| VIS → PWR, COM | Per-cell, per-hour sunlit and contact states |
| TER, PWR, COM, ICE, THM → PCL | Per-cell metrics → parcel facts |
| PCL, USE → SCR | Parcel facts + use definitions → verdicts, scores, ranking |
| SCN → SCR | Shifted time frame; upgrade rules |
| SCR → ENG | Results with IDs |
| ENG ↔ EXP | All views |
| AI ↔ ENG | Interpreted request → search → grounded results |

---

## 12. Assumptions, constraints and legal framing

**Assumptions**
- A-1. LOLA bare-terrain horizons are adequate at the chosen resolution.
- A-2. No atmosphere, so no refraction.
- A-3. Solar constant 1361 W/m² at 1 AU; reference panel is vertical and Sun-tracking.
- A-4. Surface temperatures (Diviner) are a proxy for site thermal conditions.
- A-5. The Deep Space Network is assumed available whenever Earth is in view.

**Constraints**
- C-1. Hackathon time: only H1 is built; M before S before C.
- C-2. At least one NASA data source (met).
- C-3. No paid services needed to run the core app; the AI is optional.
- C-4. The demo must not depend on live AI or network (demo mode, PRS-02).

**Legal framing**
- L-1. Under the Outer Space Treaty, the Moon is not subject to national appropriation, and private ownership of lunar land is legally unsettled. Current frameworks address using resources and operating areas, not owning land. The product therefore shows **suitability listings, not property for sale**: no prices, ownership or transactions.
- L-2. The product is neutral on who builds on the Moon (government, commercial, international) and does not advocate for any policy.

---

## 13. Acceptance criteria and demo scenario

H1 is **demo-ready** when all H1 **M** requirements are verified and this flow runs end to end, in demo mode and live:

1. **Open:** the parcel map of the south pole appears, colored by Site Score.
2. **Hover and click:** a parcel shows quick facts; clicking opens its page with score, why line, best-for tags, fact sheet, sky view (Sun skimming the real horizon) and the through-the-year chart.
3. **Search:** "Lodge" + "2028" → the map recolors; top listings appear with verdicts.
4. **Open #1:** best landing window, main risk, "not assessed" list.
5. **Go later:** +2 weeks → listings update; a change is highlighted (e.g. #1 drops, #2 rises).
6. *(S)* **Relay upgrade:** toggle → more Good parcels; the change is shown.
7. *(S)* **Describe it:** type "a fuel depot near ice in 2028" → interpretation chips → depot listings near cold traps. Same Moon, different listings.
8. **Trust:** About the data, Assumptions & limits, Horizons validation.

---

## 14. Presentation & judging

### 14.1 What judges see

A **video of up to 30 seconds** or **a deck of at most 7 slides including the title**, hosted publicly, plus the project page and possibly a live demo. The criteria are **Impact, Creativity, Validity, Relevance and Presentation**.

### 14.2 What's judgeable

| Visible in seconds (feature in the demo) | Real but invisible (mention in one line, or save for H2) |
|---|---|
| Parcel map going green / amber / red | Normalization and combining method |
| Parcel page: score, why, facts | Tie-breaking order |
| Sky view: Sun skimming the real horizon | Aggregation rules from cells to parcels |
| "Go later" → #1 drops | Data-confidence internals |
| Relay toggle → map turns greener | Weights and targets (H2 Expert mode) |
| Same Moon, different listings (lodge vs. depot) | |
| Validation plot vs. JPL Horizons | |

### 14.3 Criteria → evidence

| Criterion | Evidence |
|---|---|
| **Impact** | Anyone can use it; turns hours of specialist analysis into seconds; supports the emerging lunar economy and education; H2/H3 roadmap |
| **Creativity** | Zillow metaphor; parcel property evaluations; "what if" scenarios; describe-what-you-want AI |
| **Validity** | Terrain-aware horizons from LOLA; Horizons validation (≤ 0.1°); sanity tests; stated limits; listings-not-deeds |
| **Relevance** | Directly answers the brief: compare sites and dates; Sun/Earth vs. horizon; power and direct-to-Earth contact; time to sunset/Earthset (traceability §17) |
| **Presentation** | One clear story; strong visuals; readable on a phone |

### 14.4 Presentation requirements

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| PRS-01 | Produce both a ≤ 30 s video (primary link) and a ≤ 7-slide deck, publicly hosted, in English. | M | I |
| PRS-02 | **Demo mode:** preset scenarios (browse, lodge 2028, go later, relay, depot) that load instantly from cached results, with no AI or network dependency. | M | D |
| PRS-03 | **Presentation mode:** larger text and markers, high contrast, no developer controls, tuned for 1920×1080. | S | D |
| PRS-04 | Any main view can be captured cleanly at ≥ 1920×1080. | S | D |
| PRS-05 | The story uses **real numbers from the app**, including one before/after (e.g. "a 2-week delay drops #1 from Good to Marginal"). | M | D |
| PRS-06 | The project page and demo name the NASA datasets and how each is used. | M | I |
| PRS-07 | Backup recordings of every demo step exist before submission. | M | I |
| PRS-08 | Each milestone captures presentation assets into `docs/presentation/`. | S | I |

### 14.5 Story

**30-second video:**

| Time | Visual | Narration (draft) |
|---|---|---|
| 0–4 s | Zoom into the south pole; parcels appear | "What if you could browse the Moon like you browse homes?" |
| 4–10 s | Sky view: Sun skimming a jagged horizon; a parcel goes dark | "At the south pole, a few kilometers decides between endless sunlight and weeks of darkness." |
| 10–18 s | Search "Lodge · 2028" → map recolors → open #1: score, facts, why | "Pick what you want to build and when. Every parcel gets a property report: sunlight, nights, Earth contact, flat ground, ice." |
| 18–25 s | "+2 weeks": #1 drops. Relay toggle: map turns greener | "Plans slip? See what changes instantly — and what new infrastructure would unlock." |
| 25–30 s | Logo; "Built on NASA Horizons · LOLA · Diviner" | "[Product name]. Find your place on the Moon." |

**7 slides:**
1. **Title:** name, tagline, hero map
2. **Problem:** why the south pole is hard (sky view)
3. **The idea:** browse the Moon like homes (Zillow mapping table)
4. **Demo:** search → listings → parcel page → go later → relay
5. **Why trust it:** NASA data, terrain-aware horizons, Horizons validation, stated limits
6. **Roadmap:** H1 → H2 → H3 (figure)
7. **Vision & links:** a lunar town on the map; app, repo, video

---

## 15. Roadmap

![Product horizons](img/horizons.png)

| Horizon | Theme | Contents |
|---|---|---|
| **H1 — Hackathon** | *Browse the Moon* | Parcel grid with property evaluations; 4 use types; search → listings → parcel page; sky view; go later; relay; AI box; trust; demo |
| **H2 — Next** | *Plan with confidence* | Expert mode (weights, targets, raw data, export); comparison and shareable brief; saved searches; more use types (manufacturing, satellite assembly, relay station, rover base, resort); rover routes and reach score; more upgrades (fission power, precision landing); Earth phase and best week to visit; north pole |
| **H3 — Vision** | *Plan a lunar town* | Multi-facility development planning (pad + solar farm + depot + homes + routes); speculative infrastructure (mass drivers, manufacturing, resorts); live data; other worlds |

---

## 16. Open questions (resolve in M0 unless noted)

| # | Item | Ref |
|---|---|---|
| 1 | Product name and tagline | §1.3 |
| 2 | Area of interest; analysis-cell resolution; parcel size | §2.1, §5.1 |
| 3 | Default evaluation period | §5.2 |
| 4 | Sunlit threshold; horizon search distance | §7, HOR-01 |
| 5 | Use-type gates and targets | §5.3 |
| 6 | Verdict threshold (Good) | §7 |
| 7 | Combining method (geometric mean vs. floor penalty) | SCR-03 |
| 8 | Tie tolerance; robustness window | SCR-06/07 |
| 9 | Listing count; date-shift presets; best-times range | EXP-02, SCN-01/02 |
| 10 | AI provider and proxy hosting (by M7) | AI-06 |
| 11 | Data size budget | DAT-13 |

---

## 17. Traceability to the challenge brief

| Brief item | Requirements |
|---|---|
| Intuitive tool for planners, educators and the public | §3 (anyone), P-1–P-5, EXP-13, NFR-07 |
| Compare landing sites and dates quickly | EXP-02/03, SCN-01/02, EXP-11 |
| Curated list of notable sites plus custom coordinates | PCL-08 (named regions), EXP-05 (click anywhere) |
| Sun and Earth positions relative to the horizon | VIS-01, EXP-07 |
| Time remaining before sunset / Earthset | VIS-02, EXP-07 |
| Power generation and solar elevation | PWR-01, EXP-06/07 |
| Direct-to-Earth communication windows | COM-01, EXP-08 |
| Temporal dynamics (animation / timeline) | EXP-07/08, PCL-06 |
| Multiple visualizations (2D / 3D / creative) | EXP-01/06/07/09 |
| Use Horizons and LOLA; account for terrain; no atmosphere | EPH-01/02, TER-01, HOR-01, A-2 |
| Libration and orbital variation | EPH-01 (included in ephemeris) |
| Steep slopes and deep craters | TER-02, PCL-02, ICE-01 |
| Schedule changes force re-evaluation | SCN-01/02 |
| Educational value | Novice-first design, why lines, sky view |

---

## Appendix A — Glossary

| Term | Meaning |
|---|---|
| Parcel / analysis cell / best spot | See §7 |
| Site Score | 0–100 suitability score (§5.2, SCR) |
| Use type | What the user wants to put on a parcel (§5.3) |
| Cold trap | Surface cold enough (< 110 K) for water ice to be stable |
| PSR | Permanently shadowed region |
| LOLA | Lunar Orbiter Laser Altimeter (LRO) — terrain |
| Diviner | LRO Diviner Lunar Radiometer Experiment — temperatures |
| JPL Horizons | NASA JPL ephemeris service — Sun/Earth positions |
| LRO | Lunar Reconnaissance Orbiter |
| H1 / H2 / H3 | Hackathon / next version / vision |

## Appendix B — References

- Challenge brief: https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/
- Space Apps Project Submission Guide: https://www.spaceappschallenge.org/resources/project-submission-guide/
- JPL Horizons: https://ssd.jpl.nasa.gov/horizons/ · manual: https://ssd.jpl.nasa.gov/horizons/manual.html
- PGDA LOLA south-pole products: https://pgda.gsfc.nasa.gov/products/90 · https://pgda.gsfc.nasa.gov/products/78
- LRO Diviner data: https://www.diviner.ucla.edu/data
- Moon Trek: https://trek.nasa.gov/moon/ · Quickmap: https://quickmap.lroc.asu.edu/
- Barker et al. (2021), PSS 203, 105119. https://doi.org/10.1016/j.pss.2020.105119
- Mazarico et al. (2011), Icarus 211. https://doi.org/10.1016/j.icarus.2010.10.030
- Artemis III candidate regions (Oct 2024): https://www.upi.com/Science_News/2024/10/28/nasa-artemis-moon-landing-regions/5971730152372/
- Earlier versions: `docs/archive/requirements-v0.4.md`, `docs/archive/milestones-v0.2.md`; review: `docs/plan-review.md`
