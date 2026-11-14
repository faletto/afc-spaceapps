# Lunar Landing Site Navigator — Requirements & System Definition

*NASA Space Apps Challenge 2026 · Team afc-spaceapps*

*Version 0.4 (draft for team review) · 14 Nov 2026*

*v0.4 changes: added "At a glance", figures, and §12A Presentation & judging (PRS), after §12.*

*v0.3 changes: redefined users as a spectrum from novice to technical (§3); added experience levels (LVL, §7.22) and mission guidance heuristics (HEU, §7.23).*

*v0.2 changes: added the AI Mission Agent (AGT), its interface (AUI), the Resource Proximity subsystem (RES), and the engine tool interface (§10.1). Milestones are in `docs/milestones.md`.*


---

## 0. Document control

| Item | Value |
|---|---|
| Purpose | Define **what** the system must do and **how well**. This is the baseline for the upcoming technical design document. |
| Out of this document | Algorithms, code structure, library choices, file formats. These belong in the technical design doc. |
| Inputs | Official challenge brief and Resources tab; team planning notes; *Plan Review & Refined Requirements* (`docs/plan-review.md`) |
| Status | Draft. Open items are marked **[TBD]** and collected in §13. |

### 0.1 Requirement conventions

- **IDs.** `<SUBSYSTEM>-<NN>`, e.g. `PWR-03`. IDs are never reused.
- **Wording.** "shall" = required. "should" = desired. "may" = optional.
- **Priority (MoSCoW).**
  - **M** = Must, needed for the demo
  - **S** = Should, strongly wanted
  - **C** = Could, stretch goal
  - **W** = Won't, explicitly out of scope for the hackathon
- **Verification.**
  - **T** = Test (automated or scripted)
  - **D** = Demonstration
  - **I** = Inspection
  - **A** = Analysis (comparison against a reference)

---

## At a glance

> **Lunar Landing Site Navigator** helps anyone, from a curious student to a mission engineer, find **where and when** to land near the Moon's south pole. It shows the Sun and Earth against the **real terrain horizon**, and turns that into power, communication, terrain-safety and temperature verdicts over a whole mission. Describe a mission in plain words ("a refueling depot, sometime in 2028") and it returns a grounded shortlist of sites with rules of thumb for *why*.

| | Summary |
|---|---|
| **Problem** | At the south pole, a few km or a few days can turn 80% sunlight into 20%, and Earth contact into silence. Today's NASA tools are powerful, but slow for comparing scenarios and hard for non-specialists. |
| **Solution** | One analysis engine built on NASA data (JPL Horizons, LRO LOLA, LRO Diviner), with three detail levels and an AI mission agent on top. |
| **Users** | From people who know nothing about the Moon to concept designers who want heuristics for their mission profile to technical users who want fast screening. |
| **What makes it different** | Terrain-aware horizons (not a smooth sphere); whole-mission evaluation (not a single moment); goal-in, sites-out AI that is grounded in computed data; "what if we slip?" date exploration. |

![User spectrum](img/user-spectrum.png)

---

## 1. Purpose and problem statement

Missions to the lunar south pole face extreme, fast-changing lighting and communication conditions. Small changes in landing **location** (a few km) or **date** (a few days) can change:

- how much solar power is available,
- how long darkness lasts,
- whether Earth is visible for direct communication.

NASA tools that hold this information (JPL Horizons, Moon Trek, Quickmap) are powerful but slow to use for comparing scenarios. When a launch slips or hardware changes, planners need to re-evaluate alternative **sites** and **dates** quickly.

**The system** is an intuitive application that:

1. shows the Sun's and Earth's positions relative to the **local terrain horizon** at any south-polar site and time,
2. turns those positions into **power**, **communication**, **thermal** and **terrain-safety** metrics over a user-defined mission,
3. scores and ranks candidate sites, flags unusable ones, and supports fast comparison across sites and dates,
4. serves a **wide range of users**: from people with no lunar background, to students and concept designers who want **general heuristics** for their mission idea, to technical users who want fast quantitative screening.

**Positioning.** The system is a **heuristic screening and learning tool**. It answers "where and when, roughly, makes sense for a mission like mine, and why?" It does not replace certified mission-design analysis, and the UI says so.

---

## 2. Scope

### 2.1 In scope

- The lunar south polar region, **80°S–90°S**. The full analysis covers a core area of interest, **[TBD: 88°S–90°S or larger]**, chosen for performance.
- A curated catalog of candidate sites, plus custom coordinates.
- Mission windows within **2026-01-01 to 2030-12-31**, at **1-hour** time resolution.
- Terrain-aware Sun and Earth visibility, solar power, direct-to-Earth (DTE) comms, the surface thermal environment, and landing-terrain safety.
- A combined viability evaluation over the **entire mission duration**.
- Map overlays, a site sky view, timelines, site comparison, and date-slip exploration.
- An **AI Mission Agent**: it turns a free-text mission goal and a loose time frame into a mission profile, then into ranked candidate sites. It uses the analysis engine as tools, and every result is grounded in computed data.
- **Resource proximity** (permanently shadowed regions and cold traps) as a site metric, needed for ISRU-type and depot-type missions.

### 2.2 Out of scope (hackathon)

| Item | Reason |
|---|---|
| North polar region | Doubles the data preparation; not emphasized by the brief |
| Full equatorial/global analysis | Except optional reference sites (see SIT-04) |
| Trajectory, Δv, or "effort to reach the site" | Too far beyond the brief |
| Boulder/rock-scale hazard detection | Below DEM resolution |
| Relay-satellite comms (e.g. lunar relay orbiters) | DTE only |
| Subsurface thermal modeling (heat equation) | Replaced by measured data and a simple model |
| Detailed link budget / data-rate modeling | Rate depends on hardware, not the site |
| Rover traverse planning | Separate problem |

---

## 3. Stakeholders and users

Users form a **spectrum of expertise**, not separate groups. The same person may start as a novice and move toward expert detail. The system serves the whole spectrum from **one analysis engine**; only presentation and input depth change (§7.22).

| Level | Who | What they know | What they want | How the system serves them |
|---|---|---|---|---|
| **1. Curious / novice** | General public, younger students | Little or nothing about lunar conditions | "Show me where you could land and why it's hard" | Agent or explorer entry; Simple level; plain verdicts (good / marginal / unusable); explainer mode |
| **2. Learner / educator** | Students, teachers, outreach | Basic concepts | Understand **why** sites differ; classroom demos | Explainer, guided comparisons, animation, Simple ↔ Standard toggle |
| **3. Concept designer** (key target) | Students or teams with a mission idea, hobbyists, early-stage startups | Their mission goal, not lunar engineering parameters | **General heuristics** for their mission profile: what kinds of sites and seasons work, what constraints dominate, a shortlist of candidates | AI agent (UC-8) + mission guidance (HEU); Standard level; inferred parameters explained |
| **4. Technical user** | Engineers, planners, researchers | Mission parameters and trade-offs | Fast quantitative screening; re-plan after a slip; export | Expert level; full profile control; comparison, date sweep, raw time series, export |
| *Hackathon judges* (de facto) | | | Impact, creativity, validity, relevance, presentation | Demo flow that walks the spectrum (novice → expert); visible NASA data; stated assumptions |

**Design principles that follow from this**

- **P-1. Start simple, reveal on demand.** Every screen works at Simple level, and more detail is one click away (progressive disclosure).
- **P-2. Answers in plain words first, then numbers.** A verdict and a one-line reason come before metrics.
- **P-3. Goals in, parameters out.** Users can describe *what they want to do*. The system infers the technical inputs and shows them for review.
- **P-4. Heuristics, not just a ranked list.** Tell users *what generally works* for their profile and *what matters most*, not only which pixels scored best.
- **P-5. Same truth at every level.** Levels change presentation, never results.

---

## 4. Key use cases

| ID | Use case | Primary user level(s) |
|---|---|---|
| UC-1 | **Evaluate one site.** Pick a site and mission window → see a sky view, the sunlit/comms timeline and a metric summary. | All levels |
| UC-2 | **Find good sites.** Set a mission profile → see a map with viable areas highlighted, unusable areas in red, and the top-N sites ranked. | Concept designer, technical |
| UC-3 | **Compare sites.** Pick 2–4 sites → see their metrics and timelines side by side. | Learner, concept designer, technical |
| UC-4 | **Re-plan after a slip.** Shift the landing date, or sweep a date range → see how each site's viability changes. | Technical, concept designer |
| UC-5 | **Understand why.** Ask why site A beats site B, or why a site goes dark → get a visual and text explanation. | Novice, learner, concept designer |
| UC-6 | **Operational countdown.** Pick a moment in the mission → see time until sunset, Earthset, next sunrise and next Earthrise. | Technical, learner |
| UC-7 | **Custom site.** Enter lat/lon or click the map → run the same evaluation as for catalog sites. | All |
| UC-8 | **Goal-driven site discovery (AI agent).** Describe a mission in plain language with a loose time frame (e.g. *"I'm a student designing a propellant refueling depot near the south pole, sometime in 2028"*) → the agent infers a mission profile, asks clarifying questions if needed, searches using the analysis engine, and returns 3–5 candidate sites with landing windows, metrics and rationale. Each candidate opens in the normal views. | Novice, concept designer (primary); all levels |
| UC-9 | **Get mission heuristics.** Given a general mission profile (entered or inferred by the agent), get rules of thumb: which terrain types and seasons favor it, which constraint matters most, how much of the region is viable, and how sensitive that is to each requirement. | Concept designer, learner |

---

## 5. System overview

### 5.1 System context

![System architecture](img/architecture.png)

*Data flows left to right: NASA data → offline preparation → analysis engine → experience. The AI Mission Agent and every view call the same **engine operations**, so all results come from one source of truth.*

### 5.2 Subsystem summary

| ID | Subsystem | Responsibility | Priority |
|---|---|---|---|
| EPH | Ephemeris | Sun and Earth direction and distance relative to the Moon over time | M |
| TER | Terrain & Hazard | Elevation, slope, roughness, uncertainty; landing-safety assessment | M |
| HOR | Horizon Mask | Terrain-horizon elevation vs. azimuth for each location | M |
| VIS | Visibility | Sun and Earth az/el per site and time; visible or blocked state | M |
| PWR | Power | Solar power and energy, darkness periods | M |
| COM | Communications | Earth line-of-sight windows and gaps | M |
| THM | Thermal | Surface thermal environment over time | S |
| MSN | Mission Profile | User inputs and defaults for a mission | M |
| SIT | Site Catalog | Curated and custom sites | M |
| EVL | Evaluation | Hard constraints, viability score, ranking | M |
| MAP | Map & Overlays | Polar map, toggleable gradient layers, viable/unusable marking | M |
| SKY | Sky View | Horizon plot with Sun and Earth tracks, countdowns | M |
| TML | Timeline | Sunlit/comms bars, scrubbing, animation | M |
| CMP | Comparison | Side-by-side multi-site view | S |
| SLP | Date Sweep | Viability across candidate landing dates | S |
| RES | Resource Proximity | Distance to permanently shadowed regions (PSRs) and cold traps | S |
| EDU | Explainer | Educational mode and plain-language explanations | S |
| AGT | AI Mission Agent | Goal → mission profile → engine search → grounded candidate sites | S (core) / C (extras) |
| AUI | Agent Interface | Goal entry, inferred-profile review, clarifying questions, candidate cards, agent log | S |
| ENG | Engine Tool Interface | Callable analysis operations shared by the UI and the agent | S |
| LVL | Experience Levels | Simple / Standard / Expert presentation of the same results | M (Simple + Standard) / S (Expert) |
| HEU | Mission Guidance | Profile-level heuristics: binding constraints, sensitivity, terrain-type and seasonal patterns | S |
| EXP | Export | Export results and share scenarios | C |

---

## 6. Key definitions

These definitions are requirements in their own right. Every subsystem shall use them consistently.

| Term | Definition |
|---|---|
| **Site** | A location (lat, lon) in the area of interest, either from the catalog or user-defined. |
| **Grid cell** | One unit of the analysis raster over the area of interest; resolution **[TBD, target ≤ 240 m]**. |
| **Mission window** | [start time, start time + duration], sampled at a 1-hour step. |
| **Terrain horizon / horizon mask** | For a location, the elevation angle of the highest terrain visible in each azimuth direction, accounting for lunar curvature. |
| **Sunlit** | At a time step, the visible fraction of the solar disk above the horizon mask is > **[TBD, default 0.5]** at the reference height. |
| **Visible solar fraction** | The fraction (0–1) of the solar disk above the horizon mask. |
| **Earth in view / comms available** | Earth's center elevation exceeds the horizon mask in Earth's azimuth by at least the **antenna elevation margin**, at the antenna height. |
| **Darkness period** | A run of consecutive time steps with the site not sunlit. |
| **Comms gap** | A run of consecutive time steps with comms not available. |
| **Reference heights** | The heights above the surface for solar arrays and the antenna (mission inputs). |
| **Viable** | The site passes all hard constraints (§7.10) for the mission. |
| **Unusable** | The site fails one or more hard constraints. Shown in red. |
| **Viability score** | 0–100 weighted score of soft metrics over the mission window (§7.10). |

---

## 7. Functional requirements by subsystem

### 7.1 EPH — Ephemeris

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| EPH-01 | The system shall obtain Sun and Earth geometry relative to the Moon from **JPL Horizons**. | M | I |
| EPH-02 | Ephemeris shall cover 2026-01-01 to 2030-12-31 at a 1-hour step. | M | I |
| EPH-03 | For each time step, the system shall provide the Sun's direction and distance, and Earth's direction and distance, in a Moon-fixed frame. | M | T |
| EPH-04 | Ephemeris shall be **precomputed** and bundled; the runtime application shall not require live Horizons calls. | M | I |
| EPH-05 | Site-level Sun/Earth az/el derived by the system shall agree with direct Horizons topocentric queries (`coord@301`) within **0.1°** for at least 3 validation sites and dates. | M | A |
| EPH-06 | Earth's topocentric parallax shall be accounted for. | M | A |
| EPH-07 | Libration effects shall be inherently included (via the ephemeris), and shall be explained in explainer mode. | S | I |

### 7.2 TER — Terrain & Hazard

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| TER-01 | The system shall use **LOLA south-polar stereographic DEMs** (NASA GSFC PGDA) as the terrain source. | M | I |
| TER-02 | The system shall provide elevation, slope, and slope uncertainty for each grid cell. | M | T |
| TER-03 | The system should provide surface roughness at a lander-relevant baseline. | S | T |
| TER-04 | For a site and a user landing-ellipse radius, the system shall compute the fraction of the ellipse that meets the slope limit. | M | T |
| TER-05 | The system shall flag terrain hazards inside the ellipse: maximum slope above the limit, and elevation range above **[TBD]** m (cliff or chasm proxy). | M | T |
| TER-06 | The system shall report a terrain-data confidence indicator (from the DEM error products) for each evaluated site. | S | D |
| TER-07 | The system shall state in the UI that features below DEM resolution (e.g. boulders) are not assessed. | M | I |
| TER-08 | Terrain inputs shall be georeferenced so that a lat/lon maps to a cell with error < 1 cell. | M | T |

### 7.3 HOR — Horizon Mask

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| HOR-01 | The system shall compute a horizon mask (elevation vs. azimuth) for every grid cell in the area of interest. | M | T |
| HOR-02 | Azimuth resolution shall be ≤ **2°** for grid cells and ≤ **0.5°** for catalog sites. | M | I |
| HOR-03 | Horizon computation shall include lunar curvature and terrain out to at least **[TBD, target ≥ 50 km]**. | M | A |
| HOR-04 | Horizon masks shall support at least one height above the surface; masks at the user's reference height should be available for catalog sites. | M/S | T |
| HOR-05 | Horizon masks shall be precomputed offline and bundled. | M | I |
| HOR-06 | The mask for at least one catalog site shall be validated against an independent source (e.g. a Moon Trek or Quickmap profile, or published illumination results). | S | A |

### 7.4 VIS — Visibility

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| VIS-01 | For any site and time step, the system shall provide the Sun's and Earth's azimuth and elevation. | M | T |
| VIS-02 | For any site and time step, the system shall determine the visible solar fraction and the sunlit state (§6). | M | T |
| VIS-03 | For any site and time step, the system shall determine whether Earth is in view (§6). | M | T |
| VIS-04 | The system shall compute the times of the next sunset, sunrise, Earthset and Earthrise from any time in the mission window. | M | T |
| VIS-05 | Visibility shall be computable for **every grid cell** over the mission window, to drive the map overlays. | M | T |

### 7.5 PWR — Solar Power

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| PWR-01 | The system shall estimate solar power per time step using solar flux (scaled by Sun distance), panel area, efficiency, panel orientation, and visible solar fraction. | M | T |
| PWR-02 | Panel orientation shall default to **vertical, azimuth-tracking**, and should support a horizontal fixed option. | M/S | D |
| PWR-03 | The system shall report, over the mission: % of time sunlit, total energy (Wh), mean power (W), and **longest continuous darkness (h)**. | M | T |
| PWR-04 | The system shall report the number and lengths of darkness periods. | S | T |
| PWR-05 | If the user specifies an energy requirement, the system shall report whether it is met and by what margin. | S | T |
| PWR-06 | Without a user energy requirement, the system shall treat energy as a maximize-by-default metric in the score. | M | I |

### 7.6 COM — Direct-to-Earth Communications

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| COM-01 | The system shall determine comms availability per time step (§6) using the antenna elevation margin and antenna height. | M | T |
| COM-02 | The system shall report, over the mission: % of time comms are available, **longest comms gap (h)**, and number of comms windows. | M | T |
| COM-03 | If the user specifies a comms requirement (minimum % availability or maximum gap), the system shall evaluate it as a constraint. | S | T |
| COM-04 | Without a comms requirement, the system shall maximize comms availability by default in the score. | M | I |
| COM-05 | The system could indicate Deep Space Network coverage (Moon ≥ 10° elevation at one or more of Goldstone, Madrid or Canberra). | C | D |
| COM-06 | The UI shall present comms as **binary per time** (in the timeline and sky view) and as **% availability** on the map, not as "signal strength". | M | I |

### 7.7 THM — Thermal Environment

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| THM-01 | The system shall estimate the surface temperature environment for each site over the mission window. | S | T |
| THM-02 | The primary source shall be **LRO Diviner** polar temperature products, indexed by time of lunar day and season. | S | I |
| THM-03 | A simplified model may be used as a fallback where Diviner data are missing. The method shall be stated in the UI. | C | I |
| THM-04 | The system shall report minimum, maximum and mean temperature, and time spent below or above user limits. | S | T |
| THM-05 | Temperature limits are optional; default = no constraint. | M | I |
| THM-06 | The UI shall label this as the **surface** thermal environment, not equipment temperature. | M | I |

### 7.8 MSN — Mission Profile

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| MSN-01 | The user shall enter a **mission start date/time (UTC)** and a **mission duration**. Both are mandatory. | M | D |
| MSN-02 | If the user hasn't set a profile, the system shall apply a **default mission profile** (§7.8.1). | M | D |
| MSN-03 | Optional inputs: energy requirement; panel area, efficiency, height and orientation; antenna height and elevation margin; comms requirement; temperature limits; maximum slope; landing-ellipse radius; maximum tolerable darkness; maximum tolerable comms gap; score weights. | M/S | D |
| MSN-04 | The system shall validate inputs (ranges, the mission window within the ephemeris span) with clear error messages. | M | T |
| MSN-05 | The user should be able to save, load and name multiple profiles in the session. | S | D |
| MSN-06 | The duration shall be allowed from **1 hour to 365 days**. | M | T |

#### 7.8.1 Default mission profile

| Parameter | Default |
|---|---|
| Start | **[TBD: a 2027 date]** |
| Duration | 10 Earth days |
| Solar panels | Vertical, azimuth-tracking; height 2 m; area 1 m²; efficiency 30% |
| Antenna | Height 2 m; elevation margin 5° |
| Max slope | 10° |
| Landing ellipse radius | 100 m (≥ 95% of area within slope limit) |
| Max continuous darkness | 48 h |
| Max comms gap | None (maximize availability) |
| Temperature limits | None |
| Score weights | Power 35%, Comms 35%, Terrain margin 20%, Thermal 10% |

### 7.9 SIT — Site Catalog

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| SIT-01 | The system shall provide a catalog containing at least NASA's nine Artemis III candidate regions: Peak near Cabeus B, Haworth, Malapert Massif, Mons Mouton Plateau, Mons Mouton, Nobile Rim 1, Nobile Rim 2, de Gerlache Rim 2, Slater Plain. | M | I |
| SIT-02 | The catalog should include other notable south-polar targets (e.g. Shackleton connecting ridge, recent commercial/CLPS and international targets within 80–90°S), each with a source citation. | S | I |
| SIT-03 | The user shall add a custom site by entering lat/lon or clicking the map. | M | D |
| SIT-04 | The system could include 1–2 equatorial reference sites (e.g. Apollo 11), evaluated with a smooth-sphere horizon and clearly labeled as such, for educational contrast. | C | D |
| SIT-05 | Every catalog entry shall have a name, coordinates, a short description and a source. | M | I |

### 7.10 EVL — Evaluation & Scoring

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| EVL-01 | Evaluation shall consider the **entire mission window**, not a single moment. | M | T |
| EVL-02 | A site shall be **unusable (red)** if any hard constraint fails: (a) terrain slope/ellipse/hazard (TER-04/05); (b) longest darkness > max tolerable darkness; (c) longest comms gap > max tolerable gap (if set); (d) temperature outside limits (if set); (e) energy requirement not met (if set). | M | T |
| EVL-03 | Viable sites shall receive a **viability score (0–100)** that combines normalized metrics (energy or sunlit %, comms %, comms gap, terrain margin, thermal margin) using the user's weights. | M | T |
| EVL-04 | Normalization shall be documented, and shall be consistent across sites within one evaluation. | M | I |
| EVL-05 | For every score, the system shall show the **raw metrics** and each component's contribution. | M | D |
| EVL-06 | For unusable sites, the system shall list **which constraints failed** and by how much. | M | D |
| EVL-07 | The system shall rank sites and grid areas and identify the **top-N** (default N = 5) viable locations. | M | T |
| EVL-08 | Results shall be deterministic: the same inputs give the same outputs. | M | T |

### 7.11 MAP — Map & Overlays

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| MAP-01 | The system shall display a south-polar map (polar projection) with a terrain basemap (hillshade or imagery). | M | D |
| MAP-02 | The user shall toggle gradient overlays: **sunlit %**, **energy**, **comms availability %**, **longest darkness**, **slope / terrain hazard**, **temperature** (if THM implemented), and **viability score**. | M | D |
| MAP-03 | Unusable areas shall be shown in **red**, distinct from all gradient color scales. | M | D |
| MAP-04 | The top-N viable sites shall be marked with clear, labeled symbols (rank shown). | M | D |
| MAP-05 | Overlays shall reflect the current mission profile and window. | M | T |
| MAP-06 | Each overlay shall have a legend with units. | M | I |
| MAP-07 | Clicking the map shall show that location's metrics, with an option to add it as a custom site. | M | D |
| MAP-08 | A 3D terrain view may be provided. | C | D |
| MAP-09 | Color scales shall be colorblind-safe. | S | I |

### 7.12 SKY — Site Sky View

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| SKY-01 | For a selected site, the system shall display a sky plot of the **terrain horizon** (elevation vs. azimuth). | M | D |
| SKY-02 | The sky plot shall show the Sun's and Earth's **tracks over the mission window** and their **current positions** at the selected time. | M | D |
| SKY-03 | Track segments blocked by terrain shall be visually distinct from visible segments. | M | D |
| SKY-04 | The view shall show **countdowns**: time to next sunset/sunrise and Earthset/Earthrise from the selected time. | M | D |
| SKY-05 | The view shall show the current Sun elevation, Earth elevation, visible solar fraction and instantaneous power. | M | D |

### 7.13 TML — Timeline

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| TML-01 | For a selected site, the system shall show bars over the mission window for **sunlit/dark** and **comms/no comms**, and a power curve. | M | D |
| TML-02 | The user shall scrub the timeline. The sky view and map shall update to the selected time. | M | D |
| TML-03 | The system should play an animation of the mission window, with adjustable speed. | S | D |
| TML-04 | The timeline should mark the longest darkness and longest comms gap. | S | D |

### 7.14 CMP — Site Comparison

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| CMP-01 | The user shall select **2–4 sites** for side-by-side comparison. | S | D |
| CMP-02 | The comparison shall show each site's metrics, score, failed constraints and timeline, aligned on the same time axis. | S | D |
| CMP-03 | The best value per metric should be highlighted. | S | D |

### 7.15 SLP — Date Sweep ("What if we slip?")

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| SLP-01 | Given a range of candidate start dates and a fixed duration, the system shall compute viability for the selected sites at each candidate start. | S | T |
| SLP-02 | Results shall be shown as a **heatmap**: candidate start date × site → score, with unusable cells marked red. | S | D |
| SLP-03 | Selecting a heatmap cell shall load that site and date into the main views. | S | D |
| SLP-04 | Candidate start-date step shall default to **1 day**, over a range up to **[TBD, target 90 days]**. | S | T |

### 7.16 EDU — Explainer Mode

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| EDU-01 | The system shall offer an explainer mode with plain-language descriptions of every metric and overlay. | S | I |
| EDU-02 | The explainer shall cover at least: why the Sun skims the horizon at the pole; why terrain dominates; why Earth stays in one direction (libration); why darkness length matters more than average sunlight. | S | I |
| EDU-03 | The explainer should include a guided demo comparing two nearby sites with very different outcomes. | S | D |

### 7.17 RES — Resource Proximity

Missions such as propellant depots, ISRU (in-situ resource use) or ice prospecting need to be **near** cold, permanently shadowed terrain, while the landing site itself stays sunlit and in comms. This subsystem measures that trade-off.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| RES-01 | The system shall provide a map of permanently shadowed regions (PSRs) for the AOI, from NASA LRO-derived data. | S | I |
| RES-02 | The system shall provide a **cold-trap** map: cells whose Diviner maximum temperature is below **110 K** (a commonly used water-ice stability threshold). | S | I |
| RES-03 | For any site, the system shall report the straight-line distance to the nearest PSR and to the nearest cold trap, and the size of that region. | S | T |
| RES-04 | Resource proximity shall be usable as a **constraint** (e.g. max distance) and as a **score component** (weight, default 0 unless a mission or archetype sets it). | S | T |
| RES-05 | The map shall offer PSR and cold-trap overlays. | S | D |
| RES-06 | The system could estimate a slope-limited accessible path distance (not just straight-line) from site to resource. | C | T |
| RES-07 | The UI shall state that a PSR or cold trap indicates *potential* volatiles, not confirmed ice. | S | I |

### 7.18 AGT — AI Mission Agent

The agent is a **planner on top of the analysis engine**. It does not compute lunar geometry itself. It turns intent into engine inputs, calls engine tools (§10.1), and explains the results. Every number, site and coordinate it outputs comes from the engine.

#### 7.18.1 Goal understanding and profile inference

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| AGT-01 | The agent shall accept a free-text mission goal and an optional loose time frame (e.g. "sometime in 2028", "next year", "a 3-month window starting spring 2027"). | S | D |
| AGT-02 | The agent shall map the goal to a **mission archetype** (§7.18.4) or a custom combination, and produce a complete structured **mission profile** (all MSN-03 fields) plus search criteria (constraints and weights). | S | T |
| AGT-03 | For **every inferred value**, the agent shall give a one-line reason and mark it *inferred* (vs. *user-set*). | S | D |
| AGT-04 | When information critical to the search is missing or ambiguous (time frame, duration, crewed or robotic, power need), the agent shall ask **at most 3** clarifying questions. If the user skips them, it shall proceed with stated defaults. | S | D |
| AGT-05 | The agent shall convert a loose time frame into an explicit **search window** of candidate start dates within the ephemeris span. If a time frame is outside 2026–2030, it shall say so and propose the nearest valid window. | S | T |
| AGT-06 | The user shall be able to edit the inferred profile before or after the search. Edits shall override inferences. | S | D |

#### 7.18.2 Search, results and refinement

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| AGT-07 | The agent shall search via engine tools across the AOI grid and/or catalog sites **and** across candidate start dates in the search window, and identify the best (site, landing window) pairs. | S | T |
| AGT-08 | The agent shall return **3–5 candidate sites**, each with: name or nearest named feature, coordinates, recommended landing window(s), viability score, key metrics (sunlit %, longest darkness, comms %, longest gap, slope margin, resource distance if relevant), and failed or near-limit constraints. | S | D |
| AGT-09 | Candidates should be **spatially distinct** (configurable minimum separation, default **[TBD, e.g. 5 km]**), so the agent doesn't return five neighboring pixels. | S | T |
| AGT-10 | Each candidate shall include a plain-language **rationale** and **trade-offs** ("excellent sunlight but 9 km from the nearest cold trap"), plus what would rule it out. | S | D |
| AGT-11 | If no site satisfies all hard constraints, the agent shall say so, name the binding constraint(s), and propose specific relaxations with their effect (e.g. "allowing 72 h darkness yields 4 sites"). | S | D |
| AGT-12 | The user shall be able to refine conversationally ("prioritize comms", "move it to 2029", "only crater rims"), and the agent shall re-run only what's needed. | S | D |
| AGT-13 | The user could ask comparative or explanatory questions ("why is #1 better than #3?"), answered from engine metrics. | C | D |

#### 7.18.3 Grounding, safety and reliability

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| AGT-14 | **Grounding.** All coordinates, dates, metrics and scores shown in agent output shall come from engine tool results in the same session. The system shall **validate** agent output against engine results before display, and reject or flag mismatches. | M (if AGT is built) | T |
| AGT-15 | The agent shall not present any site as validated for real mission use. The interface shall show a disclaimer that it is an educational/planning aid. | M (if AGT is built) | I |
| AGT-16 | The agent shall decline or redirect requests outside scope (non-lunar, non-south-polar, harmful), and explain the system's scope. | S | D |
| AGT-17 | The agent's reasoning steps and tool calls shall be inspectable in a collapsible **agent log** (e.g. "Profile set → searched 248k cells × 30 dates → filtered 12 viable clusters → ranked"). | S | D |
| AGT-18 | **Evaluation set.** The team shall maintain ≥ **10** test prompts covering each archetype and edge cases. Pass criteria: inferred profiles within expected ranges for ≥ 80% of prompts; **100%** of returned candidates satisfy the hard constraints the engine reports; 0 ungrounded numbers. | S | T |
| AGT-19 | First candidate results shall appear within **≤ 30 s** of submitting a goal (excluding clarifying-question time), with progress shown during the search. | S | T |
| AGT-20 | **Fallback without an LLM.** The same flow shall be available by picking an archetype and time window from a form (no free text). This uses the identical search path (AGT-07–AGT-11), so the feature works when the LLM is unavailable. | S | D |
| AGT-21 | The core application (all non-AGT/AUI requirements) shall work with AI disabled. | M | D |
| AGT-22 | LLM credentials shall never be exposed in client code. Access shall be through a minimal server-side proxy or a user-supplied key. | M (if AGT is built) | I |
| AGT-23 | Per-session LLM usage should be bounded (max tool calls per request **[TBD]**, request rate limit) to control cost. | S | T |

#### 7.18.4 Mission archetypes

Archetypes are presets that turn a high-level goal into defaults. Values are starting points; the agent adjusts them from the goal text and the user can edit them. Exact values are **[TBD, to be validated]**.

| Archetype | Typical goal text | Duration | Key hard constraints | Score emphasis |
|---|---|---|---|---|
| **Propellant / refueling depot (ISRU)** | "refueling depot", "make fuel from ice", "propellant plant" | Long (≥ 6 months, search over the whole window) | Cold trap or PSR within **[TBD, e.g. ≤ 5 km]**; large flat area (ellipse ≥ 200 m); max darkness ≤ **[TBD]** | Continuous power, resource proximity, comms |
| **Short-stay science lander** (CLPS-like) | "drop a lander", "measure regolith", "one lunar day" | 1–14 days | Default profile | Power during the window, comms |
| **Long-duration outpost / habitat** | "base", "habitat", "crew for months" | ≥ 30 days | Large flat area; short max darkness; low comms gap | Sunlit %, comms %, thermal stability |
| **Ice prospecting rover base** | "find water ice", "rover into a crater" | 14–90 days | Resource distance ≤ **[TBD]**; accessible slope path (RES-06, if built) | Resource proximity, power |
| **Comms relay / surface station** | "relay", "radio station", "Earth link" | Long | Max comms gap ≤ **[TBD]** | Comms % and gap, power |
| **Educational demo / "what if"** | "show me", "for my class" | User or default | Default | Default; agent emphasizes explanation |

### 7.19 AUI — Agent Interface

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| AUI-01 | The landing screen shall offer two equal entry points: **"Describe your mission"** (agent) and **"Explore the map"** (manual), together with the level question (LVL-02). | S | D |
| AUI-02 | The goal input shall show 3–4 **example prompts**, including at least one student/educational example (e.g. the refueling depot). | S | I |
| AUI-03 | Clarifying questions shall be shown as **quick-reply chips**, with free text and "skip, use defaults" options. | S | D |
| AUI-04 | The inferred mission profile shall be shown as an **editable profile card**. Each field shows its value, an *inferred*/*user-set* badge and a "why" tooltip (AGT-03). Editing a field re-runs the search on confirmation. | S | D |
| AUI-05 | Results shall be shown as **candidate cards** (AGT-08, AGT-10) in rank order. Hovering a card highlights the site on the map, and the map shows all candidates with rank-numbered markers. | S | D |
| AUI-06 | Each candidate card shall have actions: **View sky** (SKY), **Timeline** (TML), **Add to compare** (CMP), **Date sweep** (SLP) and **Use this profile**. These open the standard views loaded with that site, window and profile. | S | D |
| AUI-07 | The agent panel shall show search progress with stage labels (understanding → profile → searching → ranking → explaining). | S | D |
| AUI-08 | The agent log (AGT-17) shall be available as a collapsible section. Grounding status shall be indicated (e.g. "all values verified against engine"). | S | D |
| AUI-09 | The disclaimer (AGT-15) shall be visible in the agent panel. | M (if AGT is built) | I |
| AUI-10 | When the LLM is unavailable, the panel shall switch to the archetype form fallback (AGT-20) with a clear notice. | S | D |
| AUI-11 | The agent conversation shall persist for the browser session and can be reset. | S | D |
| AUI-12 | The agent panel shall work alongside the map (docked side panel on desktop; full screen on tablet). | S | D |

### 7.20 ENG — Engine Tool Interface

The analysis engine exposes a small set of **operations** used by both the UI and the agent. This keeps one source of truth, makes the agent testable, and lets the agent and the UI be developed in parallel. These are logical operations; signatures belong in the technical design doc.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| ENG-01 | The engine shall expose these operations: **list_sites**, **get_profile_schema**, **validate_profile**, **evaluate_site** (site + profile → metrics, constraint results, score), **search_grid** (profile + constraints + region + top-N + min separation → ranked candidates), **date_sweep** (sites + start-date range + profile → score matrix), **get_site_timeseries**, **compare_sites**, and **get_resource_info**. | S | T |
| ENG-02 | Every operation shall take and return structured data (schema-defined), including units, and shall return a **result ID** that agent output can cite for grounding (AGT-14). | S | T |
| ENG-03 | Operations shall be deterministic (EVL-08) and return validation errors for invalid inputs, never silent defaults. | S | T |
| ENG-04 | The UI's own views should call the same operations, so the agent and the manual UI never disagree. | S | I |
| ENG-05 | The engine shall expose **get_mission_guidance** (profile + region + time window → HEU outputs) for both the UI and the agent. | S | T |

### 7.22 LVL — Experience Levels (progressive disclosure)

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| LVL-01 | The UI shall offer **three detail levels**: **Simple**, **Standard** and **Expert**. They can be switched at any time from a persistent control. | M (Simple, Standard) / S (Expert) | D |
| LVL-02 | On first visit, the landing screen shall ask one question to set the level (e.g. "New to this" / "I have a mission idea" / "I know the parameters"). The default if skipped is **Simple**. | S | D |
| LVL-03 | **Simple level** shall show: a verdict per site (**Good / Marginal / Unusable**, with icon and color), one plain-language reason, and at most **3 headline metrics** in everyday units (e.g. "sunlight 78% of the time", "longest night 2 days", "talk to Earth 64% of the time"). No angles, weights or raw time series. | M | I |
| LVL-04 | **Standard level** shall show all mission metrics with units and tooltips, the main profile fields (dates, duration, power need, comms need, darkness and slope limits), the sky view with numbers, and mission guidance (HEU). | M | I |
| LVL-05 | **Expert level** shall expose all MSN-03 fields and score weights, numeric horizon masks, raw time series, normalization details, data-confidence indicators and export. | S | I |
| LVL-06 | Levels shall change **presentation only**. Verdicts, scores and rankings for the same inputs shall be identical across levels (P-5). | M | T |
| LVL-07 | The Simple-level verdict mapping shall be defined: **Unusable** = fails a hard constraint; **Good** = score ≥ **[TBD, e.g. 70]**; **Marginal** = otherwise. | M | I |
| LVL-08 | Every technical term in Standard and Expert levels shall have a plain-language tooltip; Simple level shall avoid such terms entirely. | S | I |
| LVL-09 | The AI agent shall adapt its wording to the active level (e.g. no jargon at Simple level) without changing the underlying results. | S | D |

### 7.23 HEU — Mission Guidance (heuristics)

Mission guidance answers "what generally works for a mission like mine, and what matters most?" rather than "which pixel is best". All outputs are computed by the engine and stated in plain language.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| HEU-01 | For a given profile, region and time window, the system shall report the **viable fraction** of the AOI and the number of distinct viable clusters. | S | T |
| HEU-02 | The system shall identify the **binding constraint(s)**: which hard constraint eliminates the most area. Example: "longest darkness rules out 82% of the region". | S | T |
| HEU-03 | **Sensitivity.** For each key profile parameter (max darkness, max slope, comms need, power need, resource distance if used), the system shall report how the viable fraction changes if the parameter is relaxed or tightened by one defined step **[TBD steps]**. | S | T |
| HEU-04 | **Seasonality.** Within the time window, the system shall report which months or lunar days give the best and worst viability for the profile. | S | T |
| HEU-05 | **Terrain-type patterns.** The system should classify terrain into a few types (e.g. ridges/rims/massifs, slopes, crater floors, plains) and report how metrics and viability differ by type for this profile. Example: "for your profile, elevated ridges are viable 5× more often than crater floors". | S | T |
| HEU-06 | Guidance shall be presented as **3–6 plain-language rules of thumb**, each backed by the computed figure and linked to a supporting view (map overlay, sensitivity chart, seasonal chart). | S | D |
| HEU-07 | Guidance statements shall be generated from engine outputs using templates. When the AI agent phrases or extends them, the grounding rules apply (AGT-14). | S | T |
| HEU-08 | The agent shall include relevant mission guidance with its candidate list (e.g. "Why these sites: …"). | S | D |
| HEU-09 | At Simple level, guidance shall be limited to the top 2–3 rules in everyday language. | S | I |

### 7.21 EXP — Export & Sharing

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| EXP-01 | The user could export site metrics and time series as CSV. | C | D |
| EXP-02 | The user could share a scenario (sites, profile, time) via a URL. | C | D |

---

## 8. Data requirements

| ID | Dataset | Source (NASA) | Used by | Pri |
|---|---|---|---|---|
| DAT-01 | Sun/Earth ephemeris, 2026–2030, 1 h | JPL Horizons | EPH, VIS | M |
| DAT-02 | South-polar DEM (near and far field) | LRO LOLA via GSFC PGDA | TER, HOR | M |
| DAT-03 | Slope, slope error, height error | LRO LOLA via GSFC PGDA | TER | M |
| DAT-04 | Roughness | LRO LOLA via GSFC PGDA | TER | S |
| DAT-05 | Polar surface temperature (diurnal × seasonal) | LRO Diviner (PDS) | THM | S |
| DAT-06 | Basemap imagery / hillshade | Moon Trek / LOLA hillshade | MAP | M |
| DAT-07 | Site catalog coordinates | NASA Artemis announcements; mission sources | SIT | M |
| DAT-08 | Permanently shadowed region map | LRO-derived (LOLA illumination modeling / LROC PSR products) **[TBD: pick source]** | RES | S |
| DAT-09 | Cold-trap map (max temperature < 110 K) | LRO Diviner polar products | RES | S |

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| DAT-10 | The application shall use **at least one NASA data source**. This plan uses four (Horizons, LOLA, Diviner, Moon Trek). | M | I |
| DAT-11 | Every dataset shall be documented with source URL, version or date, resolution and license in a data README. | M | I |
| DAT-12 | All datasets shall share a consistent lunar reference frame and radius, and any frame differences shall be documented. | M | A |
| DAT-13 | Bundled data products should total ≤ **[TBD, target 200 MB]** for a responsive web load, with lazy loading where needed. | S | I |

---

## 9. Non-functional requirements

### 9.1 Performance

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| PERF-01 | Initial app load (on a typical laptop, broadband) ≤ **10 s** to first interactive map. | S | T |
| PERF-02 | Single-site evaluation over a 30-day window ≤ **1 s**. | M | T |
| PERF-03 | Full-grid overlay recomputation for a 30-day window ≤ **10 s**, with progress shown. | S | T |
| PERF-04 | Timeline scrubbing shall update the sky view at ≥ **20 fps**. | S | T |
| PERF-05 | Long computations shall not freeze the UI. | M | D |

### 9.2 Platform and deployment

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| PLAT-01 | The application shall run in current desktop Chrome, Firefox and Safari without installation. | M | D |
| PLAT-02 | The application should be usable on a tablet; phone use may be limited to viewing. | S | D |
| PLAT-03 | The application shall work from static hosting (e.g. GitHub Pages) with no runtime backend. **Exception:** the AI agent may use one minimal server-side proxy for LLM access (AGT-22). Everything else stays static. | S | I |
| PLAT-04 | The offline data-preparation pipeline shall be reproducible from documented scripts. | M | I |

### 9.3 Usability and accessibility

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| USE-01 | A first-time user shall reach a site evaluation (UC-1) in ≤ **3 interactions** using defaults. | M | D |
| USE-02 | All quantities shall show units; times shall be UTC with mission-elapsed time available. | M | I |
| USE-03 | Visual encodings shall not rely on color alone (patterns or labels for red/unusable). | S | I |
| USE-04 | Tooltips shall define every metric in plain language. | S | I |
| USE-05 | **Novice test:** at least 3 people with no lunar background, given only "find a good place to land a solar-powered lander next year", shall reach a site verdict and correctly explain in one sentence why it's good or bad, without help. | S | D |
| USE-06 | **Concept-designer test:** at least 2 people given a mission idea (e.g. a depot) shall obtain a candidate shortlist and state at least one correct heuristic about their profile (e.g. its binding constraint). | S | D |

### 9.4 Accuracy, transparency and integrity

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| ACC-01 | Sun/Earth angles: see EPH-05 (≤ 0.1° vs. Horizons). | M | A |
| ACC-02 | The sunlit % for at least one catalog site should be compared against published LOLA illumination results, with the difference documented. | S | A |
| ACC-03 | The application shall include an "Assumptions & Limitations" page listing all simplifications. | M | I |
| ACC-04 | The application shall credit all data sources in-app. | M | I |

### 9.5 Maintainability

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| MNT-01 | The repository shall include a README with setup, data-prep and run instructions. | M | I |
| MNT-02 | Core computations (VIS, PWR, COM, EVL) shall have automated tests against reference cases. | S | T |
| MNT-03 | Subsystems shall have defined interfaces (to be specified in the technical design doc) so they can be developed in parallel. | M | I |

---

## 10. Subsystem interfaces (logical)

These define **what information** flows between subsystems; formats are left to the technical design doc.

| From → To | Information |
|---|---|
| EPH → VIS | Time-indexed Sun and Earth direction and distance (Moon-fixed) |
| TER → HOR | Elevation grids (near and far field) |
| TER → EVL | Per-cell slope, roughness, uncertainty; per-site ellipse pass fraction and hazard flags |
| HOR → VIS | Horizon mask per cell/site (elevation vs. azimuth), per reference height |
| MSN → VIS/PWR/COM/THM/EVL | Mission window, heights, margins, panel parameters, limits, weights |
| SIT → all analysis | Site list (name, coordinates, metadata) |
| VIS → PWR | Per-time visible solar fraction, Sun elevation, Sun distance |
| VIS → COM | Per-time Earth in-view state, Earth elevation |
| VIS → SKY/TML | Per-time Sun/Earth az/el, visibility states, rise/set times |
| PWR/COM/THM → EVL | Per-site/per-cell mission metrics |
| EVL → MAP/CMP/SLP/SKY | Viable/unusable state, failed constraints, score and breakdown, ranking |
| RES → EVL | Per-site/per-cell distance to PSR and cold trap |
| ENG ↔ UI | All analysis requests from views (ENG-04) |
| AUI → AGT | Goal text, time frame, clarifying answers, profile edits, refinement requests |
| AGT → ENG | Tool calls: validate_profile, search_grid, date_sweep, evaluate_site, compare_sites, get_resource_info |
| ENG → AGT | Structured results with result IDs (for grounding) |
| AGT → AUI | Inferred profile (with reasons and badges), clarifying questions, candidate list, rationale, log, grounding status |
| AUI → MAP/SKY/TML/CMP/SLP | Hand-off of a selected candidate (site, window, profile) |

---

## 11. Assumptions and constraints

**Assumptions**

- A-1. The bare-terrain horizon from LOLA is adequate for illumination and line-of-sight at the chosen resolution.
- A-2. The lunar surface has no atmosphere, so no refraction is applied.
- A-3. Sun and Earth positions come from the ephemeris only; Earth's own surface is irrelevant except for optional DSN coverage.
- A-4. The solar constant is 1361 W/m² at 1 AU.
- A-5. The surface thermal environment is a proxy for site thermal conditions; equipment thermal design is out of scope.
- A-6. The DSN is assumed available unless COM-05 is implemented.

**Constraints**

- C-1. Hackathon timeline: features beyond **M** priority are attempted only after all **M** items work end to end.
- C-2. At least one NASA data source must be used (met by DAT-01/02).
- C-3. No paid services or credentials are required to run the app.
- C-4. Data volumes must fit static hosting and a browser.
- C-5. The AI agent depends on a third-party LLM API, so it is optional by design (AGT-20, AGT-21). The demo must not depend on live LLM availability: keep a recorded fallback of the agent flow.
- A-7. LLM outputs are probabilistic. Correctness of results is guaranteed by engine grounding (AGT-14), not by the LLM.

---

## 12. Acceptance criteria and demo scenario

The system is **demo-ready** when all **M** requirements are verified and this scenario runs end to end. The scenario deliberately walks the user spectrum, from novice to concept designer to technical user.

0. *(Novice, Simple level)* Choose "New to this" → pick Mons Mouton → see a **Good / Marginal / Unusable** verdict with three everyday metrics and one reason. Switch to Standard → the same verdict, now with full metrics.
1. Open the map → it loads with default overlays and the default mission.
2. Toggle overlays: sunlit %, comms %, slope, viability. Red areas visible; top-5 marked.
3. Select **Mons Mouton** → sky view with horizon, Sun and Earth tracks, and countdowns; timeline with sunlit/comms bars.
4. Select a nearby crater-floor point → visibly worse metrics, with failed constraints listed.
5. Change the mission start by +14 days → overlays, scores and ranking update.
6. *(S)* Compare 3 sites side by side; run a 60-day date sweep heatmap.
7. *(S)* **Agent:** enter *"I'm a student designing a propellant refueling depot near the south pole, sometime in 2028."* → answer 1–2 clarifying chips → review the inferred profile card → read the **mission guidance** rules of thumb (e.g. binding constraint, best season, best terrain type) → get 3–5 candidate cards on the map → open #1 in the sky view → add #1 and #2 to compare. Repeat with the LLM disabled, using the archetype form.
8. *(S)* Open explainer mode and show "why the Sun skims the horizon".
9. Show the Assumptions & Data Sources page with the NASA credits.

---

## 12A. Presentation & judging

The project will be judged on what judges **see**, so presentation is a requirement, not an afterthought. Space Apps submissions require a **Project Demo**: either a **video up to 30 seconds** or a **slide deck of up to 7 slides including the title slide**. It must be hosted externally with a public link. Projects are evaluated on **Impact, Creativity, Validity, Relevance and Presentation**.

### 12A.1 Judging criteria → what we show

| Criterion | Our evidence | Where it shows up |
|---|---|---|
| **Impact** | Serves the whole user spectrum (novice → engineer); answers "where and when" in seconds instead of hours; re-plans after a slip | User-spectrum figure; date-sweep heatmap; agent demo |
| **Creativity** | Goal-in, sites-out AI agent grounded in computed data; three detail levels; mission-guidance rules of thumb | Agent flow (depot prompt); Simple ↔ Expert toggle |
| **Validity** | Terrain-aware horizons from LOLA; Sun/Earth geometry validated against JPL Horizons (≤ 0.1°); illumination cross-checked with published results; limitations stated | Validation slide/plot (EPH-05, ACC-02); Assumptions page |
| **Relevance** | Every brief objective traced to a requirement (§14); NASA data used throughout | Traceability table; data-sources credits |
| **Presentation** | Clear story, strong visuals, readable on a small screen | 30 s video / 7 slides; presentation mode |

### 12A.2 Presentation requirements

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| PRS-01 | The team shall produce a submission demo that meets the Space Apps rules (video ≤ 30 s **or** ≤ 7 slides including the title slide, publicly hosted, English or English subtitles). Plan: **both**, with the video as the primary link and the deck for live or local judging. | M | I |
| PRS-02 | The project page and demo shall state **which NASA datasets** were used and **how** (Horizons → Sun/Earth geometry; LOLA → terrain and horizons; Diviner → temperatures). | M | I |
| PRS-03 | The app shall have a **demo mode** with 2–3 preset scenarios (novice site check, depot agent run, date-slip sweep) that load instantly from cached results, with no live LLM or network dependency. | S | D |
| PRS-04 | The app shall have a **presentation mode**: hides developer controls, enlarges text and markers, high contrast, layouts tuned for 16:9 at 1920×1080. | S | D |
| PRS-05 | Any main view (map, sky view, timeline, comparison, heatmap, agent results) shall be capturable as a clean **≥ 1920×1080** image without overlapping UI. | S | D |
| PRS-06 | The demo shall tell **one story** with a concrete before/after number. Example: "a student's depot idea → 4 candidate sites in 20 s; a 2-week slip drops site #1 from Good to Unusable, and the tool finds #2". The numbers must come from the app. | M | D |
| PRS-07 | A validation visual shall be produced: our Sun/Earth elevation vs. JPL Horizons over time for one site (overlaid curves plus the error). | S | D |
| PRS-08 | **Backup recordings** of every key flow shall exist before final submission (C-5). | M | I |
| PRS-09 | Documentation figures (architecture, user spectrum, roadmap) shall be reusable as slides at 16:9 without redrawing. | S | I |
| PRS-10 | Each milestone shall capture **presentation assets** (screenshots or short clips) as it completes, stored in `docs/presentation/` (see milestones doc). | S | I |

### 12A.3 Story outline (draft)

**30-second video** (≈ 75 words of narration):

| Time | Visual | Narration (draft) |
|---|---|---|
| 0–4 s | Team name; spinning south-pole terrain | "We're [team]. Landing at the Moon's south pole is a game of light and shadow." |
| 4–10 s | Sun skimming a jagged horizon in the sky view; a site flips from sunlit to dark | "A few kilometers, or a few days, can mean the difference between power and darkness, or between Earth contact and silence." |
| 10–20 s | Type "refueling depot, 2028" → profile card → candidates appear on the map | "Describe your mission. Our agent turns it into requirements and finds sites, using NASA's Horizons, LOLA and Diviner data." |
| 20–27 s | Date slip: heatmap, site #1 turns red, #2 highlighted; Simple ↔ Expert toggle | "Launch slips? See what changes instantly, at any level of detail." |
| 27–30 s | Logo + URL | "Lunar Landing Site Navigator." |

**7-slide deck:**

1. **Title.** Name, team, one-line pitch, hero image (sky view over the map).
2. **Problem.** Why the south pole is hard. Visual: Sun track vs. horizon, two nearby sites with very different numbers.
3. **Who it's for.** User-spectrum figure.
4. **How it works.** Architecture figure; NASA data called out.
5. **Demo highlights.** Agent depot flow → candidates → date slip (3 screenshots).
6. **Why trust it.** Validation plot vs. Horizons; terrain-aware vs. smooth-sphere comparison; stated limitations.
7. **Impact & next steps.** Who benefits, what's next, links (app, repo, video).

## 13. Open questions / TBD register

| # | Item | Ref | Owner | Due |
|---|---|---|---|---|
| 1 | Core analysis extent (88–90°S vs. larger) and grid resolution | §2.1, §6 | | |
| 2 | Sunlit threshold (visible solar fraction) | §6 | | |
| 3 | Horizon search distance | HOR-03 | | |
| 4 | Cliff/chasm elevation-range threshold | TER-05 | | |
| 5 | Default mission start date | §7.8.1 | | |
| 6 | Date sweep maximum range | SLP-04 | | |
| 7 | Bundled data size budget | DAT-13 | | |
| 8 | Score normalization method (e.g. min–max over AOI vs. fixed reference ranges) | EVL-04 | | |
| 9 | Which additional catalog sites (SIT-02) and their sources | SIT-02 | | |
| 10 | LLM provider/model, and proxy hosting vs. user-supplied key | AGT-22 | | |
| 11 | Archetype parameter values (depot resource distance, darkness limits, etc.) | §7.18.4 | | |
| 12 | Candidate minimum separation; max tool calls per request | AGT-09, AGT-23 | | |
| 13 | PSR data source | DAT-08 | | |
| 14 | Verdict thresholds for Simple level (Good / Marginal) | LVL-07 | | |
| 15 | Sensitivity step sizes per parameter; terrain-type classification method | HEU-03, HEU-05 | | |

---

## 14. Traceability to the challenge brief

| Brief item | Requirements |
|---|---|
| Interactive site selection, curated list, custom coordinates | SIT-01–05, MAP-07 |
| Side-by-side / sequential comparison | CMP-01–03 |
| Date and time flexibility; changes across lunar days/seasons | MSN-01, SLP-01–04, TML-02 |
| Sun & Earth position relative to the horizon | VIS-01–03, SKY-01–05 |
| Time remaining before sunset / Earthset | VIS-04, SKY-04 |
| Solar elevation, duration of sunlight, Earth visibility windows | PWR-03, COM-02, SKY-05 |
| Multiple visualization approaches (2D / 3D / other) | MAP-01–09, SKY, TML |
| Temporal dynamics (animation / timeline) | TML-01–04 |
| Accessibility across skill levels | LVL-01–09, EDU-01–03, USE-01–06, AGT/AUI (goal-driven entry), HEU (heuristics for non-specialists) |
| Help users understand why small location/date changes have large impacts | HEU-03–05, EDU-02 |
| Use JPL Horizons / precomputed datasets | EPH-01–04 |
| LOLA topography for realistic horizons | TER-01, HOR-01–06 |
| No atmosphere: horizon from terrain | HOR-01–03, A-2 |
| Solar elevation shown prominently | SKY-05 |
| Account for libration / orbital variation | EPH-03, EPH-07 |
| Steep slopes and deep craters | TER-02–05, MAP-02 |

## 15. Traceability to team plan (original notes)

| Team plan item | Disposition |
|---|---|
| Sun/Earth location data for lighting | EPH, VIS |
| Moon topography map | TER, MAP |
| Solar power generation potential | PWR |
| Moon-to-Earth comms windows | COM |
| Easy-to-use UI | USE, §12 |
| Gradients for power/comms/temperature | MAP-02 |
| Select points (poles only) | SIT-03, MAP-07; narrowed to the south pole (§2) |
| Unusable sites in red | MAP-03, EVL-02 |
| Mission duration input | MSN-01, MSN-06 |
| Landing-site safety factor / physical possibility | TER-04–07, EVL-02 |
| Temperature system | THM (Diviner instead of the heat equation) |
| Comms with DSN (simple LOS) | COM-01, COM-05 |
| Effort to reach site | Out of scope (§2.2) |
| Mission profile inputs (energy, temperature, comms) | MSN-03, PWR-05, COM-03, THM-05 |
| Comms "Speed / Reliability / Frequency of use" | Replaced by COM-02 metrics; data rate is out of scope |
| Overlays: temperature, power, comms, lighting, hazards, viability | MAP-02 (lighting and power merged) |
| Comms window binary, not gradient | COM-06 |
| Clear marking of viable regions; whole-mission evaluation | MAP-04, EVL-01 |
| Snappy, cross-platform | PERF, PLAT |
| Users: from people who don't know anything, to people who want general heuristics for their mission profile | §3 user spectrum, LVL, HEU, AGT |
| Potential AI integration | AGT, AUI, ENG: goal-driven candidate search (e.g. a student's refueling depot) with grounding and a non-LLM fallback |

---

## Appendix A — Glossary

| Term | Meaning |
|---|---|
| AOI | Area of interest |
| CLPS | Commercial Lunar Payload Services (NASA) |
| DEM | Digital Elevation Model |
| DSN | NASA Deep Space Network |
| DTE | Direct-to-Earth communication |
| Diviner | LRO Diviner Lunar Radiometer Experiment (surface temperatures) |
| LOLA | Lunar Orbiter Laser Altimeter (LRO) |
| LRO | Lunar Reconnaissance Orbiter |
| PGDA | NASA GSFC Planetary Geodesy Data Archive |
| PSR | Permanently shadowed region |
| Cold trap | Surface cold enough (max T < ~110 K) for water ice to remain stable over long periods |
| ISRU | In-situ resource utilization (e.g. making propellant from lunar ice) |
| LLM | Large language model |
| Archetype | A preset mapping a mission type (e.g. depot) to default profile values, constraints and weights |
| Grounding | Requirement that every value the agent shows comes from an engine result |
| Libration | Apparent wobble of the Moon that shifts Earth's position in the lunar sky |

## Appendix B — References

- Challenge brief: https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/
- JPL Horizons: https://ssd.jpl.nasa.gov/horizons/ · manual: https://ssd.jpl.nasa.gov/horizons/manual.html
- PGDA LOLA south-pole products: https://pgda.gsfc.nasa.gov/products/90 · https://pgda.gsfc.nasa.gov/products/78
- LRO Diviner data: https://www.diviner.ucla.edu/data
- Moon Trek: https://trek.nasa.gov/moon/ · Quickmap: https://quickmap.lroc.asu.edu/
- Barker et al. (2021), PSS 203, 105119. https://doi.org/10.1016/j.pss.2020.105119
- Mazarico et al. (2011), Icarus 211. https://doi.org/10.1016/j.icarus.2010.10.030
- Artemis III candidate regions (Oct 2024): https://www.upi.com/Science_News/2024/10/28/nasa-artemis-moon-landing-regions/5971730152372/
- Space Apps Project Submission Guide (demo format, judging criteria): https://www.spaceappschallenge.org/resources/project-submission-guide/
- Team plan review: `docs/plan-review.md`
