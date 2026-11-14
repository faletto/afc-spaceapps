# Lunar Listings — Final Requirements

*NASA Space Apps Challenge 2026 · Challenge: Lunar Landing Site Navigator · Team afc-spaceapps*

*Version 2.0 (final) · 14 Nov 2026 · Working name "Lunar Listings" (see §13)*

*This document merges the team's `Zillow on the moon planning.md` and `Zillow on the moon requirements.md` (draft v0.1) with `docs/requirements.md` v1.0. It supersedes all of them. Earlier versions are in `docs/archive/`.*

![Lunar Listings at a glance](img/personas.png)

---

## At a glance

> **The UN has started selling the Moon. Lunar Listings is the real-estate site.**
>
> It's a Zillow-style map of the Moon where every plot has a price: the **Moonstimate**. Each price is computed from real NASA data:
> - how much sunlight the plot gets,
> - how long its nights last,
> - how often it can talk to Earth,
> - how cold it gets,
> - whether it's safe to land on,
> - what's nearby.
>
> Click a plot and you see why it's priced the way it is. Zoom into the **South Pole**, the "Manhattan of the Moon", and the analysis gets serious. There, the Sun and Earth are traced against the **real terrain horizon**, because a few kilometers can mean endless sunlight or permanent darkness.

| | Summary |
|---|---|
| **Problem** | Landing-site conditions on the Moon, especially at the south pole, depend on Sun and Earth positions relative to the horizon. The tools that compute them (JPL Horizons, Moon Trek, Quickmap) are powerful but built for specialists. |
| **Idea** | Turn that science into something anyone already knows how to use: a real-estate listing site. "Bright rim lot, 82% sunlight, Earth views, cozy −230 °C basement." |
| **Users** | Anyone: curious public, students, space fans. No background needed. |
| **NASA data** | JPL Horizons (Sun and Earth positions) · LRO LOLA (terrain) · NASA Moon Trek (basemap) · LRO Diviner (temperature check, optional) |
| **Why it's different** | It's fun, and it's still rigorous: prices are reproducible and every number traces to data. South-pole lighting is terrain-aware, not "smooth Moon". You can shift the move-in date and watch prices change. |

### Fictional premise, real data

The **"UN selling the Moon"** premise is a **fictional scenario** used to make the science engaging. The app says so on screen:

> *Fictional scenario for education. In reality, the 1967 Outer Space Treaty says no nation can claim the Moon, and nobody can buy lunar land today. The prices are made up; the science is real.*

---

## 0. Document control and conventions

| Item | Value |
|---|---|
| Purpose | Final hackathon requirements: **what** to build and **how well**. Implementation details go in the technical design notes. |
| Inputs | Challenge brief + Resources; team planning notes; team requirements draft v0.1; `docs/plan-review.md`; requirements v0.4 and v1.0 |
| Status | Final for build. Remaining choices are marked **[TBD]** and listed in §13. Settle them in M0. |

**Priorities** (the team's notation):
- **P0** = required for the demo
- **P1** = strongly desired
- **P2** = stretch goal
- **Later** = roadmap only (§12); not built at the hackathon

**Verification:**
- **T** = test
- **D** = demonstration
- **I** = inspection
- **A** = analysis against a reference

### 0.1 How the two drafts were reconciled

| Topic | Team draft v0.1 | Requirements v1.0 | **Final** |
|---|---|---|---|
| Framing | UN sells the Moon; Zillow parody; prices | Zillow-style but "no prices" | **Team framing kept.** Prices are the **Moonstimate**, clearly labeled fictional (above). |
| Area | Global 1° grid + finer polar (P1) | South pole only | **Both, as two tiers:** Moon-wide (simple model) + **South Pole District** (terrain-aware). The pole is the scientific core. |
| Terrain shadowing | P2 (stretch) | Must | **P0 for the South Pole District.** The challenge brief centers on the horizon. A smooth-Moon fallback is allowed if it slips (§8). |
| Temperature | Radiative-equilibrium model (P0); heat equation and Diviner as stretch | Diviner | Team's **T1 model (P0)**, using terrain-aware sunlight at the pole; Diviner as a P1 cross-check. |
| Score | Weighted sum, safety gate, penalties | Gates → targets → combined score | **Team formula kept**, plus explicit gates and tie rules. |
| Use types | Land-type filter; weights adjustable (P2) | Four use types | **Land-type filter (P1) + "Shopping for" presets (P1)** that reweight the score. |
| Time | Time slider (P1); mission window (P2) | "Go later" scenario | **Time slider (P1) + move-in date (P1)**, so the Moonstimate changes when you shift dates. |
| Landmarks | Gazetteer, nearby list, landmark score | Named regions | **Team version** + Artemis III candidate regions. |
| AI | — | "Describe what you want" box | **P2**: "Ask the realtor". |
| Presentation | ~3-minute demo script | 30 s video / 7 slides | **Both** (§11). |

---

## 1. Goals and non-goals

### 1.1 Goals

1. **Educate through play.** A user with no space background should understand, within a couple of minutes, why the south pole is prime real estate and the far side is "cheap but off-grid".
2. **Be scientifically grounded.** Every price traces back to real NASA data and a documented formula. Key geometry is validated against JPL Horizons.
3. **Answer the challenge brief.** Compare sites and dates; show the Sun and Earth relative to the horizon; assess power and direct-to-Earth comms; show time until sunset or Earthset.
4. **Feel like Zillow.** A familiar layout and familiar interactions, so the parody lands instantly.
5. **Be demoable.** Loads fast and works offline, with no live API dependency on stage.

### 1.2 Non-goals

- Mission-grade landing-site certification.
- Real transactions, accounts or payments.
- Real legal claims about owning the Moon. The premise is fictional.
- Trajectory or fuel-cost modeling ("effort to reach the site"). It's in the roadmap only.
- Full-resolution global analysis in the browser.

---

## 2. Users

| Persona | Description | What they need |
|---|---|---|
| **Curious public** (primary) | Interested in space, no technical background | Fun hook, plain-language explanations, no jargon |
| **Students** (high school to early undergrad) | Learning about the Moon, physics or data science | Visible formulas and data sources, "learn more" links |
| **Space enthusiasts** | Follow Artemis, know some terms | Real site names, candidate-region comparison, accurate overlays |
| **Hackathon judges** | Assessing impact, creativity, validity, relevance, presentation | A clear story, obvious NASA data use, a working demo |

**Design principles**

- **D-1.** Every number has a one-sentence plain-English explanation on hover or click.
- **D-2.** Everyday units first, e.g. "sunlight 82% of the year", "longest night 4.6 days". Technical units go in tooltips.
- **D-3.** If a feature needs a tutorial, it's P2 or Later.
- **D-4.** Be honest about limits. Say what is and isn't modeled.

---

## 3. User stories

| ID | As a… | I want to… | So that… | Pri |
|---|---|---|---|---|
| US-1 | visitor | see a map of the Moon covered in price tags | I get the concept immediately | P0 |
| US-2 | visitor | click a price tag and see the plot's listing | I understand what makes it valuable | P0 |
| US-3 | visitor | toggle temperature / sunlight / comms / hazard overlays | I can see *why* some areas cost more | P0 |
| US-4 | visitor | filter by price range | I can find "affordable" or "luxury" plots | P0 |
| US-5 | visitor | jump into the South Pole District | I can explore the most interesting real estate in detail | P0 |
| US-6 | visitor | see the Sun and Earth moving around a plot's horizon | I understand light, darkness and Earth contact | P0 |
| US-7 | visitor | filter by land type (mare, highlands, crater rim, PSR, peak of light, far side…) | I can compare terrain types | P1 |
| US-8 | visitor | scrub a time slider and watch lighting and comm windows change | I understand the Moon's day/night cycle and libration | P1 |
| US-9 | visitor | change the move-in date and see prices change | I understand that timing matters as much as location | P1 |
| US-10 | visitor | pick what I'm shopping for (lander, home base, solar farm, ice depot) | prices reflect my use | P1 |
| US-11 | student | see the formula and data source behind each number | I can learn the science | P1 |
| US-12 | visitor | see nearby landmarks (Apollo sites, famous craters, Artemis regions) | plots feel like real places | P1 |
| US-13 | visitor | compare two plots side by side | I can choose between them | P2 |
| US-14 | enthusiast | adjust how much each factor matters | I can find *my* ideal plot | P2 |
| US-15 | visitor | ask the realtor in plain words ("a sunny spot near ice") | I don't need to learn the filters | P2 |
| US-16 | visitor | share a link to a plot | I can show friends | P2 |

---

## 4. System overview

![System architecture](img/architecture.png)

*Offline Python pipeline → static files → static web app. The browser never calls Horizons and never downloads the full DEM.*

### 4.1 Two tiers

| | **Moon-wide** | **South Pole District** |
|---|---|---|
| Purpose | The hook: near side vs. far side, maria vs. highlands | The core: what the challenge asks for |
| Area | Whole Moon | 80°S–90°S (core area **[TBD, e.g. 85–90°S]**) |
| Plot size | 1° × 1° (≈ 30 km at the equator) **[TBD]** | ≈ 1 km × 1 km in polar stereographic **[TBD]** |
| Sunlight and Earth contact | **Smooth-Moon** model: Sun and Earth elevation from the sub-solar and sub-Earth points | **Terrain-aware**: Sun and Earth vs. the real horizon from LOLA (HOR) |
| Terrain data | LOLA global DEM, downsampled | LOLA south-polar products (stereographic, higher resolution) |
| Labeled in the UI as | "Moon-wide estimate" | "Detailed survey" |

### 4.2 Subsystems

| ID | Subsystem | Responsibility | Pri |
|---|---|---|---|
| EPH | Ephemeris | Sub-solar point, sub-Earth point, Sun and Earth distance over the analysis window (Horizons) | P0 |
| GRID | Plots | Global and polar plot grids; IDs, bounds, aggregation | P0 |
| SAFE | System A: landing safety | Slope, roughness, relief, landing-safe flag, hazard score | P0 |
| HOR | Terrain horizons | Horizon elevation vs. azimuth for polar cells | P0 (polar) |
| SOL | System B: solar power | Sunlit fraction, energy, longest darkness, time series | P0 |
| TEMP | System C: temperature | T1 radiative-equilibrium temperatures; thermal hazard | P0 |
| COMM | System D: Earth comms | Earth-visible fraction, longest blackout, windows | P0 |
| LAND | Land type & landmarks | Land-type classification; gazetteer; nearby list; landmark score | P1 |
| ICE | Ice access (polar) | Permanently shadowed regions from our own lighting results; distance to nearest | P1 |
| VS | Viability score | Combined 0–100 score; gates; presets; ties | P0 |
| PRICE | Moonstimate | Price from viability and premiums; "why" line | P0 |
| SCN | Scenarios | Move-in date shift; relay upgrade (P2) | P1 |
| UI | Web app | Map, price markers, listing panel, sky view, overlays, filters, time slider | P0 |
| TRU | Trust | Data sources, formulas, validation, fictional-premise disclaimer | P0 |
| AI | Ask the realtor | Plain-language search (grounded) | P2 |
| PRS | Presentation | Demo mode, presentation mode, assets | P0 |

---

## 5. Functional requirements: interface

### 5.1 Layout (Zillow parody)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [Logo] Search crater/region…  [Shopping for ▾] [Price ▾] [Land type ▾]   │
│                               [Overlays ▾]  [Move-in: 2028 ▾]            │
├─────────────────────────────────────────────┬────────────────────────────┤
│  LUNAR MAP (pan / zoom)    [Moon-wide | South Pole] │ ┌──────────────────┐ │
│     [$1.2M]        [$340K]                  │ │ plot imagery     │ │
│            [$8.9M]       [$75K]             │ └──────────────────┘ │
│   ┌ overlay legend ┐                        │ $4,200,000 Moonstimate │
│   │ ▓▓▓▒▒░░ sun    │                        │ Shackleton Rim · Plot 12│
│   └────────────────┘                        │ ★ Viability 87/100     │
│  ◀━━━━━━━━●━━━━━━━━▶ time slider            │ "Bright rim lot…"      │
│                                             │ ── Facts & features ── │
│                                             │ ── Sky view ──         │
│                                             │ ── Price history ──    │
└─────────────────────────────────────────────┴────────────────────────────┘
```

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| UI-1 | Two-column layout: **left** = interactive lunar map; **right** = listing panel for the selected plot. | P0 | D |
| UI-2 | A recognizable Zillow **parody** (price-pill markers, listing card, "Facts & features", estimate badge) **without** Zillow's name, logo or assets in the product branding. | P0 | I |
| UI-3 | The fictional-premise disclaimer (see "At a glance") is visible on first load and in the footer. | P0 | I |
| UI-4 | Responsive down to 1280 px laptop width. Mobile is not required. | P1 | D |
| UI-5 | When nothing is selected, the right panel shows 2–3 **featured listings** (e.g. a polar rim plot, a far-side bargain, an Apollo-adjacent plot). | P1 | D |

### 5.2 Map

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| MAP-1 | Global lunar basemap (Moon Trek imagery or LOLA hillshade) with pan and zoom. A static fallback image is available offline. | P0 | D |
| MAP-2 | A **price marker** for each visible plot; markers cluster or aggregate at low zoom. | P0 | D |
| MAP-3 | Hovering a marker highlights the plot boundary; clicking selects it and fills the listing panel. The selection persists while overlays and filters change. | P0 | D |
| MAP-4 | A **South Pole District** view in polar stereographic projection, reachable with one click (tab or inset). | P0 | D |
| MAP-5 | Plots that fail the landing-safety gate show a distinct "Not buildable" marker style (not color alone). | P0 | D |
| MAP-6 | A landmark label layer (named craters, Apollo/Luna/Chang'e landing sites, NASA's Artemis III candidate regions), toggleable. | P1 | D |
| MAP-7 | Search box that jumps to a named feature (e.g. "Shackleton", "Tranquility Base"). | P2 | D |

### 5.3 Listing panel

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| DET-1 | Plot name or ID, nearest named feature, center lat/lon, tier label ("Moon-wide estimate" or "Detailed survey"). | P0 | D |
| DET-2 | **Moonstimate** price and a one-line **why** ("Priced high for near-constant sunlight and Earth views"). | P0 | D |
| DET-3 | **Viability Score** (0–100) with a bar per factor (safety, power, comms, thermal, landmarks). | P0 | D |
| DET-4 | **Facts & features** in everyday units: sunlight % of year; longest night; Earth contact %; longest blackout; temperature min/mean/max (°C, K in tooltip); mean and P90 slope; buildable area %; landing-safe flag; land type; ice nearby (polar). | P0 | D |
| DET-5 | **Sky view (polar plots):** the plot's terrain horizon with the Sun's and Earth's paths. Segments blocked by terrain look different. Shows **time until next sunset / Earthset** at the time-slider position. | P0 | D |
| DET-6 | **Listing blurb** generated from thresholds, e.g. "Bright, south-facing rim lot with 24/7 Earth views. Cozy −230 °C basement (PSR) next door." | P1 | D |
| DET-7 | **Price history** parody chart: the Moonstimate month by month through the analysis year, driven by monthly sunlight and comms. | P1 | D |
| DET-8 | Tooltips on every fact: plain-language explanation, then (P1) formula and data source. | P0/P1 | I |
| DET-9 | **Nearby** landmarks within N km, with distances. | P1 | D |

### 5.4 Filters and "Shopping for"

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| FIL-1 | Filter by price range. Plots outside the range are hidden or dimmed. | P0 | D |
| FIL-2 | Filter by land type (multi-select): Mare · Highlands · Crater floor · Crater rim · PSR · Peak of light · Far side. | P1 | D |
| FIL-3 | "Buildable only" toggle. | P1 | D |
| FIL-4 | **Shopping for** presets: *Any (default)* · *First lander* · *Home base* · *Solar farm* · *Ice depot*. Each preset changes score weights and gates (§6.8) and re-prices the map. | P1 | D |
| FIL-5 | Minimum sunlight % and minimum Earth contact % sliders. | P2 | D |
| FIL-6 | Filter state reflected in the URL. | P2 | T |

### 5.5 Overlays

One gradient overlay is active at a time. Each has a legend with units and a one-line explanation.

| ID | Overlay | Type | Value | Pri |
|---|---|---|---|---|
| OV-1 | Sunlight | Gradient | % of time sunlit (terrain-aware at the pole) | P0 |
| OV-2 | Earth contact | Gradient | % of time Earth is above the cutoff (terrain-aware at the pole) | P0 |
| OV-3 | Temperature | Gradient | Mean surface temperature (toggle mean / min / max) | P0 |
| OV-4 | Terrain hazards | Gradient | Slope, with the hazard threshold highlighted | P0 |
| OV-5 | Viability | Gradient | Combined score 0–100 | P0 |
| OV-6 | Longest night | Gradient | Longest continuous darkness (hours) | P1 |
| OV-7 | Comm window | **Binary**, time-dependent | Earth visible / not visible at the slider time | P1 |
| OV-8 | Ice access (polar) | Gradient | Distance to nearest PSR | P1 |

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| OV-9 | Perceptually uniform, colorblind-safe palettes (diverging for temperature). | P0 | I |
| OV-10 | Overlay opacity slider. | P1 | D |

### 5.6 Time and scenarios

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| TIME-1 | Time slider across the analysis window (default one year, **[TBD: 2028]**), with hourly data in the polar tier and 6-hourly at least in the Moon-wide tier. | P1 | D |
| TIME-2 | The comm-window overlay, the instantaneous sunlit/dark view, and the sky view's Sun and Earth positions update with the slider. | P1 | D |
| TIME-3 | Play/pause animation. | P2 | D |
| SCN-1 | **Move-in date:** choose a start date and stay length (e.g. 2 weeks, 3 months, 1 year). Stats and the Moonstimate for the selected plot, and (P2) the whole map, are recomputed for that window. Changes are highlighted, e.g. "Price ↓ 35%: arriving 2 weeks later means a 5-day night." | P1 | D |
| SCN-2 | **Relay upgrade:** a toggle that assumes a relay satellite. Earth-contact penalties are removed and prices update, with the change shown neutrally. | P2 | D |

---

## 6. Functional requirements: data and scoring

All heavy computation happens **offline** in a re-runnable Python pipeline that outputs static files.

### 6.1 EPH: ephemeris

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| EPH-1 | Query JPL Horizons **once per quantity** for the analysis window: target `301` (Moon), observer `500@399` (geocenter), `QUANTITIES='14,15,19,20'` (sub-Earth point, sub-solar point, Sun range, Earth range), hourly. Cache the responses to disk and commit them. | P0 | I |
| EPH-2 | For any location, compute Sun and Earth elevation and azimuth from the sub-solar and sub-Earth points, using the local east-north-up frame. Earth parallax is included for the polar tier. | P0 | T |
| EPH-3 | **Validation:** compare with direct Horizons topocentric queries (`CENTER='coord@301'`, `QUANTITIES='4'`) at 3 or more sites (near side, limb, south pole) on 3 or more dates. Pass: ≤ **0.1°** with parallax (polar method); ≤ **1°** for the smooth Moon-wide method. | P0 | A |
| EPH-4 | Horizons use is polite: cached, no parallel hammering, back off on errors. | P0 | I |

### 6.2 GRID: plots

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| GRID-1 | **Moon-wide grid:** 1° × 1° plots (configurable). | P0 | I |
| GRID-2 | **South Pole District grid:** ≈ 1 km plots in polar stereographic, built from finer analysis cells (≈ 240 m **[TBD]**). | P0 | I |
| GRID-3 | Each plot has a stable ID, center lat/lon, boundary polygon, tier, and all computed attributes. | P0 | T |
| GRID-4 | Grid resolutions are single config values. | P0 | I |
| GRID-5 | Plot values are aggregated from cells by documented rules (e.g. buildable area = share of safe cells; sunlight = value at the plot's best cell), with a consistency test. | P0 | T |

### 6.3 SAFE: System A, landing safety

**Inputs:**
- Moon-wide: LOLA global DEM (USGS `Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif`), downsampled.
- Polar: LOLA south-polar stereographic DEM and slope products (NASA GSFC PGDA).

**Method:** slope from the elevation gradient; roughness = standard deviation of elevation in a window; relief = max − min within the plot. Aggregate per plot.

**Outputs:** `slope_mean_deg`, `slope_p90_deg`, `safe_area_frac`, `roughness_m`, `relief_m`, `landing_safe`, `hazard_score`.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| SAFE-1 | Safe-slope threshold configurable; default **8°**. | P0 | I |
| SAFE-2 | `landing_safe = safe_area_frac ≥ 0.25` (configurable). | P0 | T |
| SAFE-3 | `hazard_score` = normalized combination of P90 slope, roughness and relief. | P0 | T |
| SAFE-4 | The listing states that boulder-scale hazards are below the data resolution. | P0 | I |

### 6.4 HOR + SOL: System B, sunlight and solar power

**Irradiance:** `TSI = L_sun / (4π R²)`, with L_sun = 3.828 × 10²⁶ W and R = Sun–Moon distance. TSI varies between ~1320 and ~1412 W/m² over the year. (The planning notes call this "atmospheric pressure"; it is irradiance, and the Moon has no atmosphere.)

**Visibility:**
- Moon-wide: the Sun is up when `e_sun > 0` (smooth Moon).
- Polar: the Sun is up when it clears the **terrain horizon** in its direction. Use the visible fraction of the solar disk, because the disk is ~0.53° wide and at the pole the Sun skims the horizon.

**Flux:**
- Horizontal surface: `F = TSI · max(0, sin e_sun) · V`.
- Vertical Sun-tracking panel (the polar default): `F = TSI · V`.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| HOR-1 | Precompute each polar analysis cell's **terrain horizon**: elevation vs. azimuth in ≤ 2° steps, including lunar curvature and terrain out to **[TBD, ≥ 50 km]**. | P0 (polar) | T |
| HOR-2 | Cross-check one site's horizon against an independent profile (Moon Trek or Quickmap). | P1 | A |
| SOL-1 | Compute TSI from the Sun–Moon distance at each step. | P0 | T |
| SOL-2 | Per plot over the window: `sunlit_frac`, mean flux, `energy_wh_m2_per_day`, `longest_dark_hours`, `longest_light_hours`; plus a downsampled time series for charts. | P0 | T |
| SOL-3 | Reference array power `P = F · A · η` (default A = 10 m², η = 0.30). | P1 | T |
| SOL-4 | **Fallback:** if HOR slips, the polar tier uses the smooth-Moon model, labeled "simplified lighting". Accept this only as a last resort; it weakens the south-pole story. | — | I |

### 6.5 TEMP: System C, temperature

**T1 model (P0):**
- Day: `T_day = [(1 − A)·F(t) / (εσ)]^¼`, with A ≈ 0.12, ε ≈ 0.95, σ = 5.67 × 10⁻⁸.
- Night floor: ≈ 95–100 K (equatorial); ≈ 40 K in PSRs.
- At the pole, `F(t)` uses terrain-aware sunlight.

For reference, the 1D heat equation `∂/∂z(k ∂T/∂z) = ρc ∂T/∂t` uses **z = depth**, not latitude. It's a stretch goal.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| TEMP-1 | Per plot: temperature min, mean and max over the window, using T1. | P0 | T |
| TEMP-2 | `thermal_hazard_score` penalizes extreme cold and large swings; thresholds in config. | P0 | T |
| TEMP-3 | Tooltip explains the ~300 °C day/night swing (no atmosphere; long lunar day). | P1 | I |
| TEMP-4 | Cross-check polar T1 results against **LRO Diviner** polar temperatures for a few plots, and document the differences. | P1 | A |
| TEMP-5 | Heat-equation (T2) model. | P2 | T |

### 6.6 COMM: System D, Earth communication

**Assumption:** simple line of sight. Comms are available when Earth's center is above the cutoff, and, at the pole, above the terrain horizon. The DSN's three complexes (Goldstone, Madrid, Canberra) are treated as continuous coverage. Relay satellites are out of scope, except for the SCN-2 scenario.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| COMM-1 | Elevation cutoff configurable; default **5°**. | P0 | I |
| COMM-2 | Per plot: `earth_visible_frac`, `longest_blackout_hours`, `mean_earth_elevation_deg`, `comms_score`. | P0 | T |
| COMM-3 | Per-timestep visibility for the comm-window overlay, at reduced resolution. | P1 | T |
| COMM-4 | Polar comms are terrain-aware (via HOR). | P0 (polar) | T |

### 6.7 LAND + ICE: land types, landmarks, ice

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| LAND-1 | Primary land type per plot from elevation, slope, latitude and lighting (e.g. `sunlit_frac ≈ 0` → PSR; very high sunlight near the pole → Peak of light; lon beyond ±90° → Far side). | P1 | T |
| LAND-2 | Landmarks from the IAU/USGS Gazetteer of Planetary Nomenclature, plus a curated list of Apollo/robotic landing sites and the nine Artemis III candidate regions (Peak near Cabeus B, Haworth, Malapert Massif, Mons Mouton Plateau, Mons Mouton, Nobile Rim 1, Nobile Rim 2, de Gerlache Rim 2, Slater Plain). | P1 | I |
| LAND-3 | `landmark_score` from proximity to notable features. | P1 | T |
| ICE-1 | Polar plots: PSRs derived from **our own** terrain-aware lighting (`sunlit_frac = 0` over the year); distance to the nearest PSR reported as "Ice access". | P1 | T |
| ICE-2 | Tooltip: PSRs may hold water ice, but it's not confirmed. | P1 | I |
| LAND-4 | Refine land type using the USGS Unified Geologic Map. | P2 | T |

### 6.8 VS + PRICE: viability and the Moonstimate

**Viability (0–100):**

```
viability = 100 · Σ wᵢ·sᵢ / Σ wᵢ          (only if all gates pass)

s_safety   = 1 − hazard_score
s_power    = normalize(energy_wh_m2_per_day) · penalty(longest_dark_hours)
s_comms    = earth_visible_frac · penalty(longest_blackout_hours)
s_thermal  = 1 − thermal_hazard_score
s_landmark = landmark_score
s_ice      = proximity to PSR (polar only; weight 0 unless a preset sets it)
```

**Default weights:** Safety 0.30 · Power 0.25 · Comms 0.20 · Thermal 0.15 · Landmarks 0.10.

**Gates:** `landing_safe = false` → "Not buildable", and viability is capped at **[TBD, e.g. 10]**. Presets may add gates, e.g. *Home base*: longest blackout ≤ **[TBD]** h.

**"Shopping for" presets (FIL-4):**

| Preset | Weight changes | Extra gates |
|---|---|---|
| Any | Defaults | — |
| First lander | Safety ↑, Power ↑ | Longest night ≤ 48 h |
| Home base | Comms ↑, Thermal ↑ | Longest blackout ≤ **[TBD]** h |
| Solar farm | Power ↑↑ | Buildable area ≥ **[TBD]** % |
| Ice depot | Ice ↑↑, Power ↑ | Ice access ≤ **[TBD, e.g. 10]** km (polar only) |

**Moonstimate:**

```
price = BASE · exp(k · viability/100) · (1 + landmark_premium) · scarcity_multiplier
```

- `BASE` ≈ $50,000; `k` tuned so the top plots reach the low millions and the worst the low thousands.
- Premiums: e.g. +25% within 50 km of an Apollo site; +50% for Peak-of-light rim plots.
- Rounded to real-estate numbers ($1.25M, $340K).

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| VS-1 | Weights, normalization bounds, penalties, gates and presets live in one config file. | P0 | I |
| VS-2 | Normalization uses **fixed reference ranges**, not ranges relative to what's on screen, so scores mean the same everywhere. | P0 | I |
| VS-3 | Breakdown shown in the listing (DET-3). | P0 | D |
| VS-4 | Scores within ±2 are labeled **tied**. Tie-break order: (1) smaller score change across move-in dates; (2) larger safety margin; (3) plot ID. | P1 | T |
| VS-5 | **Sanity tests** run automatically (see §9). | P0 | T |
| VS-6 | User-adjustable weights in the UI. | P2 | D |
| PRICE-1 | Price is deterministic from plot attributes + config. No randomness. | P0 | T |
| PRICE-2 | One-line price explanation (DET-2). | P0 | D |

---

## 7. Data sources

| Source | Agency | Used for | Pri |
|---|---|---|---|
| **JPL Horizons API** (`https://ssd.jpl.nasa.gov/api/horizons.api`, docs: `https://ssd.jpl.nasa.gov/api.html`) | NASA/JPL | Sub-solar and sub-Earth points, Sun and Earth distances, validation queries | P0 |
| **LOLA global DEM** (USGS `Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif`) | NASA LRO / USGS | Moon-wide slope, roughness, relief, land type | P0 |
| **LOLA south-polar products** (NASA GSFC PGDA, e.g. `LDEM_80S_*`, `LDSM_80S_*`) | NASA LRO | Polar terrain, horizons, slope | P0 |
| **NASA Moon Trek** (Trek API, WMTS tiles) | NASA | Basemap imagery/hillshade (static fallback for offline) | P0 |
| **IAU/USGS Gazetteer of Planetary Nomenclature** | IAU / USGS | Landmark names and coordinates | P1 |
| **NASA Artemis III candidate regions** (Oct 2024 announcement) | NASA | Landmark layer | P1 |
| **LRO Diviner** polar temperatures | NASA LRO | Temperature cross-check | P1 |
| USGS Unified Geologic Map of the Moon | USGS | Land-type refinement | P2 |
| Thermal model paper (ScienceDirect S009457652500517X) | — | Heat-equation reference | P2 |

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| DAT-1 | A data README documents each source's URL, version, resolution and license, and how to reproduce the derived products. | P0 | I |
| DAT-2 | One lunar reference frame and radius throughout; any differences documented. | P0 | A |
| DAT-3 | Large files (DEMs) are downloaded once, never shipped to the client, and not committed (use a download script). | P0 | I |

---

## 8. Non-functional requirements

| ID | Requirement | Target | Pri |
|---|---|---|---|
| NFR-1 | Initial load to an interactive map | < 3 s on a laptop over decent Wi-Fi | P0 |
| NFR-2 | Overlay toggle / filter response | < 200 ms | P0 |
| NFR-3 | Time slider scrub (comm window, sky view) | ≥ 15 fps | P1 |
| NFR-4 | Static payload, excluding basemap tiles | < 25 MB core (polar detail lazy-loaded) **[TBD]** | P0 |
| NFR-5 | **Offline demo mode**: runs fully from local files with a static basemap | Required | P0 |
| NFR-6 | Pipeline re-runnable end to end with one command, using cached API responses | Required | P0 |
| NFR-7 | Accessibility: colorblind-safe palettes; keyboard-focusable markers; status not by color alone | Best effort | P1 |
| NFR-8 | Every displayed metric documents its units and source | Required | P0 |
| NFR-9 | Static hosting (GitHub Pages, Netlify or Vercel). The only exception is a tiny proxy if the P2 AI is built. | Required | P0 |

---

## 9. Acceptance criteria (MVP)

**Experience**
- [ ] A first-time user selects a plot and reads its price and three key facts within **30 seconds**, unaided.
- [ ] The South Pole District opens in one click and shows the sky view for a polar plot.
- [ ] The fictional-premise disclaimer is visible.
- [ ] The app runs from local static files with the network disabled.

**Science sanity checks** (automated where possible)
- [ ] Near-side plots show `earth_visible_frac ≈ 1.0`; far-side centers ≈ 0.0; limb and polar plots are intermediate.
- [ ] Equatorial plots: `sunlit_frac ≈ 0.5`; longest darkness ≈ 14–15 Earth days (~355 h).
- [ ] TSI stays within ~1320–1412 W/m² across the year.
- [ ] Equatorial T1: daytime max ≈ 390 K; night ≈ 95–100 K.
- [ ] Horizons validation passes (EPH-3).
- [ ] Polar: known permanently shadowed crater interiors (e.g. Shackleton's floor) show `sunlit_frac ≈ 0`; known well-lit rim and ridge areas rank in the top tier.
- [ ] Steep crater walls are flagged "Not buildable".

---

## 10. Interfaces and data contracts

**Pipeline outputs**
- `plots_global.json` and `plots_polar.json` (one entry per plot):
  ```json
  { "id": "SP-0412", "tier": "polar", "lat": -89.4, "lon": 132.0, "bounds": [[...]],
    "name": "Shackleton Rim · Plot 12", "land_type": "crater_rim",
    "price_usd": 4200000, "viability": 87,
    "scores": {"safety":0.91,"power":0.95,"comms":0.61,"thermal":0.55,"landmark":0.9,"ice":0.8},
    "facts": {"slope_mean_deg":4.2,"slope_p90_deg":9.8,"safe_area_frac":0.62,"landing_safe":true,
              "sunlit_frac":0.82,"energy_wh_m2_per_day":21500,"longest_dark_hours":110,
              "temp_min_k":70,"temp_mean_k":190,"temp_max_k":330,
              "earth_visible_frac":0.61,"longest_blackout_hours":260,"ice_km":3.1},
    "nearby": [{"name":"Shackleton","km":8.1}],
    "blurb": "Bright rim lot with near-constant sun…",
    "monthly": {"sunlit":[...],"earth":[...],"price":[...]} }
  ```
- Overlay rasters (PNG with a known ramp, or single-band data colored in the client).
- Polar horizons for featured and selected plots (for the sky view); comm-window bitsets.
- Ephemeris table (subsampled) for client-side sky view and slider.

**Frontend:** reads only static files; no runtime API calls (except the P2 AI proxy).

**Recommended stack (team to confirm):**
- Pipeline: Python (`numpy`, `rasterio`/GDAL, `requests`, `pandas`).
- Frontend: React or plain TypeScript with Leaflet (custom coordinate systems) or MapLibre/deck.gl; Recharts or Chart.js for charts.
- Hosting: GitHub Pages, Netlify or Vercel.

---

## 11. Presentation and judging

Judges see a **video of up to 30 seconds** or a **deck of up to 7 slides including the title**, publicly hosted, plus the project page and possibly a live demo. They score on **Impact, Creativity, Validity, Relevance and Presentation**. The full script and slides are in `docs/presentation.md`.

| Criterion | Evidence we show |
|---|---|
| Impact | Anyone can explore lunar landing science; it turns specialist data into something people want to click; education plus the emerging lunar economy |
| Creativity | The Zillow parody, the Moonstimate, listing blurbs, price history, the "move-in date" twist |
| Validity | NASA Horizons + LOLA; terrain-aware polar lighting; Horizons validation; sanity checks; formulas shown; fictional premise labeled |
| Relevance | Compare sites and dates; Sun and Earth vs. the horizon; power and direct-to-Earth comms; time to sunset/Earthset |
| Presentation | One story, strong visuals, a 30 s video plus a 7-slide deck |

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| PRS-1 | A ≤ 30 s video (primary link) and a ≤ 7-slide deck, public links, English. | P0 | I |
| PRS-2 | **Demo mode:** featured plots and scenarios preloaded, offline. | P0 | D |
| PRS-3 | **Presentation mode:** larger text and markers, no dev controls, 1920×1080. | P1 | D |
| PRS-4 | The story uses **real numbers from the app** (prices, sunlight %, before/after a move-in shift). | P0 | D |
| PRS-5 | The project page names the NASA datasets and how each is used. | P0 | I |
| PRS-6 | Backup recordings of every demo step. | P0 | I |
| PRS-7 | Screenshots or clips captured at every milestone into `docs/presentation/`. | P1 | I |

### Live demo script (~3 minutes)

1. Open the global map: *"The UN is selling the Moon. Here's the listings site."*
2. Click a cheap far-side plot: *"Great price… zero Earth contact, two-week nights."*
3. Toggle **Earth contact**: the near side lights up and the far side goes dark.
4. Jump to the **South Pole District**, toggle **Sunlight**: peaks of light glow and PSRs are black.
5. Click a Shackleton rim plot: a multi-million Moonstimate, with the breakdown, blurb and **sky view** (the Sun skimming the jagged horizon, time until sunset).
6. Shift the **move-in date**: the price drops and the listing says why.
7. Close: *"Every price is computed from NASA data, terrain-aware at the pole, and validated against JPL Horizons."*

---

## 12. Roadmap (not built at the hackathon)

![Roadmap](img/horizons.png)

| Next | Vision |
|---|---|
| Ask the realtor (AI), user-adjustable weights, compare and share | Plan a lunar town: pad + solar farm + depot + homes + rover routes, evaluated together |
| More "Shopping for" types: manufacturing, relay station, rover base, resort | Speculative infrastructure (mass drivers, manufacturing) |
| Rover routes and a "commute score" | Live data from new missions; other worlds (Mars) |
| Relay and fission-power upgrades across the whole map; Earth phase and "best week to visit" | |
| North pole District; effort-to-reach (Δv) estimate | |

---

## 13. Open questions (resolve in M0)

| # | Question | Suggested default |
|---|---|---|
| 1 | Public product name | "Lunar Listings" (alternatives: Moonstimate, Crater & Barrel Realty). No "Zillow" in branding. |
| 2 | Analysis year | 2028 (Artemis-era) |
| 3 | Grid sizes | 1° global; ~1 km polar; ~240 m polar analysis cells |
| 4 | Polar core area | 85–90°S, extend if time allows |
| 5 | Comms cutoff | 5° |
| 6 | Price per plot or per km²? | Per plot (simpler to read; plot area shown) |
| 7 | Preset gate values; not-buildable cap; tie tolerance | Set in config at M0 |
| 8 | Frontend framework and map library | Team choice |
| 9 | Horizon search distance | ≥ 50 km |

---

## Appendix A: Glossary

| Term | Meaning |
|---|---|
| **Moonstimate** | Our parody price estimate for a plot |
| **Viability Score** | Our combined 0–100 rating |
| **Plot** | A grid cell users browse (1° Moon-wide; ~1 km at the pole) |
| **South Pole District** | The detailed, terrain-aware polar tier |
| **Terrain horizon** | The skyline seen from a spot; at the pole it decides sunlight and Earth contact |
| **TSI** | Total Solar Irradiance: solar power per m² at a given distance from the Sun |
| **PSR** | Permanently Shadowed Region: never sunlit; extremely cold; may hold water ice |
| **Peak of (near-)eternal light** | High polar terrain that's sunlit most of the year |
| **Sub-solar / sub-Earth point** | The point on the Moon directly beneath the Sun / Earth |
| **Libration** | The Moon's apparent wobble, which makes Earth visibility intermittent near the limb and poles |
| **DSN** | NASA Deep Space Network |
| **LOLA / LRO / Diviner** | Lunar Orbiter Laser Altimeter / Lunar Reconnaissance Orbiter / LRO's thermal radiometer |

## Appendix B: References

- Challenge brief: https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/
- Space Apps Project Submission Guide: https://www.spaceappschallenge.org/resources/project-submission-guide/
- JPL Horizons: https://ssd.jpl.nasa.gov/horizons/ · API docs: https://ssd.jpl.nasa.gov/api.html
- USGS LOLA global DEM: https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif
- PGDA LOLA south-pole products: https://pgda.gsfc.nasa.gov/products/90
- NASA Moon Trek API: https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=moon
- LRO Diviner data: https://www.diviner.ucla.edu/data
- Artemis III candidate regions (Oct 2024): https://www.upi.com/Science_News/2024/10/28/nasa-artemis-moon-landing-regions/5971730152372/
- Thermal model: https://www.sciencedirect.com/science/article/abs/pii/S009457652500517X
- Team sources: `Zillow on the moon planning.md`, `Zillow on the moon requirements.md`; earlier versions in `docs/archive/`
