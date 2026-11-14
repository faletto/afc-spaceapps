# Lunar Listings — Requirements v2.2 (final)

| | |
|---|---|
| **Event** | NASA Space Apps Challenge 2026 · Challenge: Lunar Landing Site Navigator · Team afc-spaceapps |
| **Version** | 2.2 (final) · 14 Nov 2026 |
| **Location** | `docs/requirements.md` (moved here from the repo root, `Zillow on the moon requirements.md`, with its git history) |
| **Builds on** | v2.1 (team revision aligning with Zillow) and v2.0 (merged final) |
| **Supersedes** | v2.1, v2.0, draft v0.1 and all `Lunar-Navigator-*` docs. Earlier versions are in `docs/archive/` and `Claude outputs/archive/`. |
| **Source of truth** | **This file.** Markdown, so changes show up in git diffs. The `.docx` in `Claude outputs/` is an export of it. The technical specification is `docs/technical-spec.md`. |
| **Working name** | "Lunar Listings" (see §13) |

---

## What changed in v2.2 (final)

v2.2 keeps everything in v2.1 and fixes the problems found when reviewing it. Changed rows are tagged **[v2.2]**.

| # | Fix | Where | Why |
|---|---|---|---|
| **F1** | **Home-type gates are calibrated so every type returns results.** Night and blackout gates are checked over the type's **reference stay** (Lander pad: 14 days; Habitat: 90 days; Solar farm and Ice depot: the full year), at the plot's best move-in date in the analysis year. Gate values are tuned in M3 so each type returns at least **[TBD, e.g. 50]** plots in the South Pole District. | §6.8, FIL-4 | In v2.1, "longest night ≤ 48 h" was checked over a whole year. Every equatorial plot has ~355 h nights and even the best polar ridges have multi-day nights over a year, so "Lander pad" would have shown about 0 results. |
| **F2** | **The relay upgrade never changes the Buy price.** It shows a separate "With relay: $X" what-if value next to the Moonstimate. | SCN-2 | v2.1's D-6 and its acceptance test say the Buy price never changes with UI state, but SCN-2 said "prices update." |
| **F3** | **"Average rent" has one definition:** `rent_avg_usd_month` = the Rent Moonstimate for a 1-year stay = `RENT_RATIO · Buy price`. The Price cut badge compares against it. | §6.8, DET-11 | v2.1 used "yearly average rent" for the badge and "1-year rent" for RENT-5. Averaging monthly rents doesn't equal the 1-year rent, because the price formula is nonlinear. |
| **F4** | **The scarcity cutoff is stored in config** (the viability value at the top N%), so rent can be computed in the browser with the same price function. | §6.8, VS-1 | The scarcity multiplier depends on a plot's rank among all plots, which the browser can't compute for one plot. |
| **F5** | **"Earth view" badge only where it means something:** polar and limb plots with Earth contact ≥ 95%. | DET-11 | On the near side Earth contact is ~100% everywhere, so v2.1's rule put the badge on half the Moon. |
| **F6** | **Results list is virtualized and capped** (render at most **[TBD, e.g. 200]** cards; sorted; "Showing 200 of 1,284"). | RES-1 | The Moon-wide grid alone has ~65,000 plots; rendering every card would break the 200 ms target (NFR-2). |
| **F7** | **Terrain horizons ship for every South Pole District plot**, lazy-loaded by map tile, so any plot's 3D Tour works. Size budgeted in NFR-4. | §10, NFR-4 | v2.1 shipped horizons only for featured and selected plots, but "selected" can be any plot. |
| **F8** | Small consistency fixes: the price-range example now matches ±10% ($3.8M–$4.6M); "360° Tour" is the fallback name if "3D Tour" is challenged; doc locations resolved (former open question 12). | §5.1, glossary, §13 | — |

---

## What changed in v2.1

**The guiding rule for this revision is to stick to Zillow as closely as possible.** If Zillow already has a pattern for something, we use that pattern instead of inventing a new UI. A judge or first-time visitor should recognize every screen within a second, and each recognized pattern is one less thing to explain in a 30-second video.

v2.0 merged two drafts well. The team draft had the Zillow parody and prices. The Navigator draft had terrain-aware polar science and a sky view. v2.1 kept **all of v2.0's science, data pipeline, milestones and P0 scope**. It changes how several features are presented so they behave like Zillow, fixes two places where v2.0 contradicts itself, and restores one overlay the planning notes asked for.

Requirements that changed or are new are tagged **[v2.1]** in the tables below.

### Change log

| # | Change | Where | Why |
|---|---|---|---|
| **C1** | **Buy / Rent tabs.** v2.0 changed a plot's Moonstimate when you shifted the move-in date (SCN-1). Now the **Buy** tab shows a fixed annual Moonstimate, and the move-in date and stay length move to a **Rent** tab that shows a **Rent Moonstimate** for that stay. | §5.1, §5.6 (new RENT-1…4 replace SCN-1), §6.8 | **Zillow fit:** on Zillow, a home's Zestimate doesn't change depending on when you plan to move in. Rentals, though, have an "available / move-in date," and Zillow puts Buy and Rent side by side as top-level tabs. **Consistency:** in v2.0, the price changed with the time slider (SCN-1) and also with the month (DET-7), so the price on the pin wasn't a stable fact about the plot. **Demo:** we keep the "arrive 2 weeks later → cheaper" beat, now phrased as rent. |
| **C2** | **"Shopping for" presets become Zillow's *Home type* filter plus a *Best match* sort.** Presets no longer re-price the map. They filter by their gates and rank plots with a **match %**. | §5.4 (FIL-4 rewritten, FIL-7 new), §6.8 | **Zillow fit:** Zillow's Home type filter (Houses, Condos, Lots/Land…) narrows results and never changes prices. In v2.0, choosing "Solar farm" changed every price on the map, which makes the price look like an opinion instead of a fact about the land. **Consistency:** this also keeps PRICE-1 ("deterministic from plot attributes + config") true regardless of UI state. |
| **C3** | **Sky view is renamed "3D Tour"** and is presented as a 360° panorama tab in the listing gallery. The underlying feature is unchanged: terrain horizon, Sun and Earth paths, time to sunset/Earthset. | §5.3 (DET-5) | **Zillow fit:** a 360° skyline seen from the plot *is* a 3D home tour. "Sky view" needs explaining, while "3D Tour" is a button people already know to click. No extra engineering. |
| **C4** | **Factor scores shown as Zillow-style named scores** (like Walk Score / Transit Score): Landing Score, Sun Score, Signal Score, Comfort Score, Views Score, Ice Score. The math is unchanged. | §5.3 (DET-3), §6.8 | **Zillow fit:** Zillow listings show numeric neighborhood ratings as named 0–100 scores. "Signal Score 61" reads instantly; "s_comms = 0.61" doesn't (design principle D-2). |
| **C5** | **Results list of listing cards** in the right column, with a result count and a Sort dropdown. Clicking a card or pin opens the listing, with "← Back to results." | §5.1 (UI-1 revised, UI-5 replaced), §5.7 (new RES-1…4) | **Zillow fit:** Zillow search is a map *plus a card grid*. That card grid is the most recognizable part of Zillow after the price pins. v2.0 only showed 2–3 featured cards in the empty panel. This is still compatible with the planning notes ("right column is data on the highlighted property"): selecting a plot still fills the right column with its data. |
| **C6** | **Facts line under every price**: `82% sun · 61% Earth · 4° slope · 1.0 km²`, the lunar version of "3 bd · 2 ba · 1,850 sqft." | §5.3 (DET-10), §5.7 | **Zillow fit:** this line is Zillow's signature element. v2.0's slide 3 speaker notes already pitch "beds and baths are sunlight and Earth contact," but no requirement defined it. |
| **C7** | **Moonstimate range** ("$3.9M – $4.5M"), like the Zestimate range. Width comes from the tier's uncertainty (P1), or from the LOLA error layers (P2). | §5.3 (DET-2), §6.8 (PRICE-3) | **Zillow fit:** every Zestimate shows a range. **Honesty:** this supports D-4 ("be honest about limits"). Moon-wide plots get a wider range than "Detailed survey" polar plots, which shows the two-tier quality difference without extra text. |
| **C8** | **Listing badges**: *Hot property*, *Earth view*, *Peak of light*, *Price cut* (Rent), *Off market*. All are computed from data with fixed thresholds. | §5.3 (DET-11), §6.8 | **Zillow fit:** Zillow cards carry status badges ("New listing," "Price cut"). They make the card grid scannable, and they come straight from fields we already compute. |
| **C9** | **Not-buildable plots appear "Off market"** as grey dots, not price pins. | §5.2 (MAP-5) | **Zillow fit:** Zillow shows off-market homes as grey dots. This is the same meaning as v2.0's "Not buildable" with a symbol people already know, and it still doesn't rely on color alone. |
| **C10** | **Dots when zoomed out, price pills when zoomed in.** | §5.2 (MAP-2) | **Zillow fit:** this is Zillow's zoom behavior. **Performance:** it also handles the "too many markers" risk better than unspecified clustering. |
| **C11** | **Solar power overlay restored** (energy, Wh/m²/day). | §5.5 (OV-11) | The planning notes list *Solar Power Generation potential* and *Lighting characteristics* as separate overlays. v2.0 kept "Sunlight %" and "Longest night" but dropped the energy overlay. The data (`energy_wh_m2_per_day`, SOL-2) is already computed, so this is nearly free. |
| **C12** | **Disclaimer worded like Zillow's Zestimate fine print.** | "At a glance," §5.1 (UI-3) | Same legal and ethical content as v2.0, but in Zillow's voice, so it adds to the parody instead of interrupting it. |
| **C13** | **"Contact agent" button opens "Ask the realtor," plus a save/heart button and a mortgage-payment parody** (all P2). | §5.3 (DET-12…14) | **Zillow fit:** these sit on every Zillow listing. All are stretch work (P2) and don't affect the MVP. |
| **C14** | **Tie-break rules (VS-4) moved from P1 to P2.** | §6.8 | Users and judges never see tie-break order, so effort is better spent on visible P1 items (C5–C8). The ±2 "tied" label can return if time allows. |
| **C15** | **Price history becomes "Rent history"** (monthly Rent Moonstimate across the analysis year). | §5.3 (DET-7), §10 | This follows from C1: the Buy price is annual and fixed, so monthly change belongs to rent. The chart, data and demo value are the same. |
| **C16** | **Housekeeping**: this markdown file is the canonical spec; the `Lunar-Navigator-*.docx` files are superseded; v2.0 paths that don't exist in the repo (`docs/requirements.md`, `docs/archive/`, `docs/presentation.md`) are flagged. | Header, §13 | v2.0 points to files that aren't in the repo, and two sets of `.docx` docs sit side by side. One diffable source avoids the team building from different versions. |

**Not changed:** two tiers (Moon-wide + South Pole District), terrain-aware polar lighting and comms (P0), the ephemeris method and Horizons validation, Systems A–D, ICE, the viability formula and default weights, the Moonstimate formula, data sources, NFRs, acceptance criteria (plus additions), the presentation strategy, and the roadmap.

**Follow-ups in other docs** (applied in v2.2 to `docs/milestones.md`, `docs/presentation.md` and the deck):
- **Milestones**
  - M3 gains the results list, facts line, Off-market dots and the zoom-dependent markers (C5, C6, C9, C10).
  - M4 ships the sky view as the 3D Tour (C3).
  - M5 gains Home type and sort, named scores, badges and the price range (C2, C4, C7, C8).
  - M6's move-in date work becomes the Rent tab (C1, C15).
- **Presentation plan**
  - Video 0:12–0:21 calls the sky view "3D Tour."
  - Video 0:21–0:26 says "Rent ↓ XX% if you move in 2 weeks later."
  - Slide 3's Zillow-to-Moon mapping table should list: Zestimate → Moonstimate, Rent Zestimate → Rent Moonstimate, beds/baths/sqft → sun/Earth/slope/km², 3D Tour → horizon panorama, Walk Score → Sun/Signal Score, Home type → Lander pad/Habitat/Solar farm/Ice depot, Off market → not buildable.

---

## At a glance

The UN has started selling the Moon. **Lunar Listings** is the real-estate site.

It's a Zillow-style map of the Moon where every plot has a price, the **Moonstimate**. Each price is computed from real NASA data:
- how much sunlight the plot gets,
- how long its nights last,
- how often it can talk to Earth,
- how cold it gets,
- whether it's safe to land on,
- what's nearby.

Browse listings the way you'd browse homes: price pins on a map, a grid of listing cards, a listing page with "Facts & features," a **3D Tour**, and named scores. Want a short stay instead? Switch to **Rent**, pick a move-in date, and see what that stay costs. Zoom into the **South Pole District**, the "Manhattan of the Moon," and the analysis gets serious. There, the Sun and Earth are traced against the real terrain horizon, because a few kilometers can mean endless sunlight or permanent darkness.

### Summary

| | |
|---|---|
| **Problem** | Landing-site conditions on the Moon, especially at the south pole, depend on where the Sun and Earth are relative to the horizon. The tools that compute this (JPL Horizons, Moon Trek, Quickmap) are powerful but built for specialists. |
| **Idea** | Turn that science into something everyone already knows how to use: a real-estate listing site. "Bright rim lot, 82% sun, Earth views, cozy −230 °C basement." |
| **Users** | Anyone: curious public, students, space fans. No background needed. |
| **NASA data** | JPL Horizons (Sun and Earth positions) · LRO LOLA (terrain) · NASA Moon Trek (basemap) · LRO Diviner (temperature cross-check, optional) |
| **Why it's different** | Fun and rigorous at the same time: prices are reproducible and every number traces to data. South-pole lighting is terrain-aware, not "smooth Moon." Rent a plot for a different week and watch the price change. |

### Fictional premise, real data

The "UN selling the Moon" premise is a fictional scenario to make the science engaging. **[v2.1]** The app says so in Zillow-style fine print:

> *The Moonstimate is Lunar Listings' estimated market value for a plot. It is not an appraisal, and it is fictional: under the 1967 Outer Space Treaty no nation can claim the Moon, and nobody can buy lunar land today. The prices are made up; the science behind them is real.*

---

## 0. Document control and conventions

| Item | Value |
|---|---|
| Purpose | Final hackathon requirements: what to build and how well. Implementation details go in the technical design notes. |
| Inputs | Challenge brief and Resources; team planning notes (`Zillow on the moon planning.md`); draft v0.1; Navigator plan review; requirements v1.0 and v2.0 |
| Status | Final for build. Remaining choices are marked [TBD] and listed in §13. Settle them in M0. |

**Priorities**
- P0 = required for the demo
- P1 = strongly desired
- P2 = stretch goal
- Later = roadmap only (§12); not built at the hackathon

**Verification**
- T = test
- D = demonstration
- I = inspection
- A = analysis against a reference

**[v2.1]** / **[v2.2]** = new or changed in that version (see the change logs).

### 0.1 Zillow ↔ Lunar Listings mapping **[v2.1]**

This table is the design reference: before inventing UI, check whether Zillow already has it.

| Zillow | Lunar Listings | Req |
|---|---|---|
| Map with price pins; dots when zoomed out | Lunar map with Moonstimate pins; dots when zoomed out | MAP-2 |
| Results card grid, "N results," Sort | Plot cards, "N results," Sort | RES-1…4 |
| Buy / Rent tabs | Buy / Rent tabs | UI-6, RENT-* |
| Zestimate (+ range) | Moonstimate (+ range) | DET-2, PRICE-3 |
| Rent Zestimate | Rent Moonstimate | RENT-2 |
| Rental move-in date | Move-in date + stay length | RENT-1 |
| 3 bd · 2 ba · 1,850 sqft | 82% sun · 61% Earth · 4° slope · 1.0 km² | DET-10 |
| Facts & features | Facts & features (everyday units) | DET-4 |
| 3D Home Tour | 3D Tour (360° horizon with Sun and Earth paths) | DET-5 |
| Walk Score / Transit Score | Landing / Sun / Signal / Comfort / Views / Ice Score | DET-3 |
| Home type filter | Home type: Lander pad · Habitat · Solar farm · Ice depot | FIL-4 |
| Neighborhood | District (Moon-wide, South Pole District) and land type | MAP-4, FIL-2 |
| Nearby schools / points of interest | Nearby landmarks (Apollo sites, Artemis III regions, craters) | DET-9 |
| Badges: New listing, Price cut | Badges: Hot property, Earth view, Peak of light, Price cut | DET-11 |
| Off-market grey dots | "Off market" = not buildable | MAP-5 |
| "Homes for you" | "Plots for you" (featured listings) | RES-4 |
| Price history | Rent history (monthly) | DET-7 |
| Zestimate disclaimer fine print | Fictional-premise fine print | UI-3 |
| Contact agent | Ask the realtor (AI) | DET-12 |
| Save ♡ / Est. payment | Save ♡ / Est. payment parody | DET-13, DET-14 |

**Branding rule (unchanged):** copy Zillow's *layout and patterns*, never its name, logo, colors or assets.

---

## 1. Goals and non-goals

### 1.1 Goals
- **Educate through play.** A user with no space background should understand, within a couple of minutes, why the south pole is prime real estate and the far side is "cheap but off-grid."
- **Be scientifically grounded.** Every price traces back to real NASA data and a documented formula. Key geometry is validated against JPL Horizons.
- **Answer the challenge brief.** Compare sites and dates; show the Sun and Earth relative to the horizon; assess power and direct-to-Earth comms; show time until sunset or Earthset.
- **Feel like Zillow.** **[v2.1]** Use Zillow's patterns wherever one exists (§0.1), so the parody lands instantly and needs no tutorial.
- **Be demoable.** Loads fast and works offline, with no live API dependency on stage.

### 1.2 Non-goals
- Mission-grade landing-site certification.
- Real transactions, accounts or payments.
- Real legal claims about owning the Moon. The premise is fictional.
- Trajectory or fuel-cost modeling ("effort to reach the site"). Roadmap only.
- Full-resolution global analysis in the browser.

---

## 2. Users

| Persona | Description | What they need |
|---|---|---|
| Curious public (primary) | Interested in space, no technical background | Fun hook, plain-language explanations, no jargon |
| Students (high school to early undergrad) | Learning about the Moon, physics or data science | Visible formulas and data sources, "learn more" links |
| Space enthusiasts | Follow Artemis, know some terms | Real site names, candidate-region comparison, accurate overlays |
| Hackathon judges | Assessing Impact, Creativity, Validity, Relevance, Presentation | A clear story, obvious NASA data use, a working demo |

### Design principles
- **D-1.** Every number has a one-sentence plain-English explanation on hover or click.
- **D-2.** Everyday units first, e.g. "sunlight 82% of the year," "longest night 4.6 days." Technical units go in tooltips.
- **D-3.** If a feature needs a tutorial, it's P2 or Later.
- **D-4.** Be honest about limits. Say what is and isn't modeled.
- **D-5. [v2.1]** If Zillow has a pattern for it, use that pattern (§0.1).
- **D-6. [v2.1]** A plot's Buy price is a fact about the plot. It never changes with UI state (filters, home type, time slider). Only the Rent price depends on a chosen stay.

---

## 3. User stories

| ID | As a… | I want to… | So that… | Pri |
|---|---|---|---|---|
| US-1 | visitor | see a map of the Moon covered in price tags | I get the concept immediately | P0 |
| US-2 | visitor | click a price tag or listing card and see the plot's listing | I understand what makes it valuable | P0 |
| US-3 | visitor | toggle temperature / sunlight / comms / hazard overlays | I can see why some areas cost more | P0 |
| US-4 | visitor | filter by price range | I can find "affordable" or "luxury" plots | P0 |
| US-5 | visitor | jump into the South Pole District | I can explore the most interesting real estate in detail | P0 |
| US-6 | visitor | take a 3D Tour and see the Sun and Earth moving around a plot's horizon **[v2.1]** | I understand light, darkness and Earth contact | P0 |
| US-17 | visitor | scroll a list of listing cards and sort it **[v2.1]** | I can browse the way I would on a real-estate site | P0 |
| US-7 | visitor | filter by land type (mare, highlands, crater rim, PSR, peak of light, far side…) | I can compare terrain types | P1 |
| US-8 | visitor | scrub a time slider and watch lighting and comm windows change | I understand the Moon's day/night cycle and libration | P1 |
| US-9 | visitor | switch to Rent, pick a move-in date and stay length, and see the rent change **[v2.1]** | I understand that timing matters as much as location | P1 |
| US-10 | visitor | pick a home type (lander pad, habitat, solar farm, ice depot) and sort by best match **[v2.1]** | I find plots that suit my use | P1 |
| US-11 | student | see the formula and data source behind each number | I can learn the science | P1 |
| US-12 | visitor | see nearby landmarks (Apollo sites, famous craters, Artemis regions) | plots feel like real places | P1 |
| US-13 | visitor | compare two plots side by side | I can choose between them | P2 |
| US-14 | enthusiast | adjust how much each factor matters | I can find my ideal plot | P2 |
| US-15 | visitor | ask the realtor in plain words ("a sunny spot near ice") | I don't need to learn the filters | P2 |
| US-16 | visitor | share a link to a plot, or save it | I can show friends or come back later | P2 |

---

## 4. System overview

**Architecture:** offline Python pipeline → static files → static web app. The browser never calls Horizons and never downloads the full DEM.

```
┌────────────────────────── Offline pipeline (Python) ───────────────────────────┐
│ Horizons API ──► ephemeris cache (sub-solar pt, sub-Earth pt, Sun/Earth range) │
│ LOLA global DEM ──► downsample ─► slope / roughness / relief (Moon-wide)        │
│ LOLA polar DEMs ──► slope + terrain horizons (South Pole District)              │
│ Gazetteer + Artemis III regions ──► landmarks                                   │
│        ▼                                                                       │
│ Systems A–D + ICE per plot ─► scores ─► viability ─► Moonstimate (+range, rent) │
│        ▼                                                                       │
│ plots_global.json, plots_polar.json, overlays, horizons, time series, bitsets  │
└────────────────────────────────────────────────────────────────────────────────┘
                     │ static files
                     ▼
┌──────────────────────── Static web app ────────────────────────────────────────┐
│ Map + pins · results cards · listing (facts, scores, 3D Tour) · Buy/Rent ·      │
│ filters/sort · overlays · time slider                                          │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Two tiers

| | Moon-wide | South Pole District |
|---|---|---|
| Purpose | The hook: near side vs. far side, maria vs. highlands | The core: what the challenge asks for |
| Area | Whole Moon | 80°S–90°S (core area [TBD, e.g. 85–90°S]) |
| Plot size | 1° × 1° (≈ 30 km at the equator) [TBD] | ≈ 1 km × 1 km in polar stereographic [TBD] |
| Sunlight and Earth contact | Smooth-Moon model: Sun and Earth elevation from the sub-solar and sub-Earth points | Terrain-aware: Sun and Earth vs. the real horizon from LOLA (HOR) |
| Terrain data | LOLA global DEM, downsampled | LOLA south-polar products (stereographic, higher resolution) |
| Labeled in the UI as | "Moon-wide estimate" | "Detailed survey" |
| Moonstimate range width **[v2.1]** | Wide (default ±25%) | Narrow (default ±10%) |

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
| VS | Viability score | Combined 0–100 score; named scores **[v2.1]**; gates; home-type match **[v2.1]** | P0 |
| PRICE | Moonstimate | Buy price from viability and premiums; range **[v2.1]**; "why" line | P0 |
| RENT **[v2.1]** | Rent Moonstimate | Stay-specific rent from a move-in window (replaces v2.0 SCN-1 re-pricing) | P1 |
| SCN | Scenarios | Relay upgrade (P2) | P2 |
| UI | Web app | Map, pins, results list **[v2.1]**, listing, 3D Tour, overlays, filters, time slider | P0 |
| TRU | Trust | Data sources, formulas, validation, fictional-premise disclaimer | P0 |
| AI | Ask the realtor | Plain-language search (grounded) | P2 |
| PRS | Presentation | Demo mode, presentation mode, assets | P0 |

---

## 5. Functional requirements: interface

### 5.1 Layout (Zillow parody) **[v2.1]**

**Search view** (default):

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ [Logo]   [ Buy | Rent ]   Search crater or region…                            │
│ [Price ▾] [Home type ▾] [Land type ▾] [More ▾] [Overlays ▾]                   │
│                                  (Rent only:) [Move-in: Mar 3, 2028 ▾] [Stay ▾]│
├──────────────────────────────────────────┬───────────────────────────────────┤
│ LUNAR MAP   [Moon-wide | South Pole]     │ Lunar real estate                  │
│                                          │ 1,284 results  Sort: Price ↓ ▾     │
│    •  •  [$1.2M]     [$340K]   •         │ ┌──────────────┐ ┌──────────────┐  │
│        [$8.9M]    ●(grey) off market     │ │ [img] HOT    │ │ [img]        │  │
│   ┌ legend ┐                             │ │ $4.2M        │ │ $340K        │  │
│   │▓▓▒▒░░ sun│                           │ │ 82% sun·61%  │ │ 50% sun·0%   │  │
│   └────────┘                             │ │ Earth·4°·1km²│ │ Earth·6°·900…│  │
│  ◀━━━━━━━●━━━━━━━▶  time slider          │ │ Shackleton…  │ │ Far side…    │  │
│                                          │ └──────────────┘ └──────────────┘  │
└──────────────────────────────────────────┴───────────────────────────────────┘
```

**Listing view** (after clicking a pin or card; replaces the card grid in the right column):

```
┌──────────────────────────────────────────┬───────────────────────────────────┐
│ LUNAR MAP (selected plot highlighted)    │ ← Back to results          ♡ Save  │
│                                          │ [ Photos | 3D Tour ]               │
│                                          │ $4,200,000   HOT PROPERTY          │
│                                          │ 82% sun · 61% Earth · 4° · 1.0 km² │
│                                          │ Shackleton Rim · Plot 12           │
│                                          │ Moonstimate $3.8M–$4.6M  ⓘ         │
│                                          │ "Bright rim lot with near-constant…"│
│                                          │ ── Scores ──  Sun 92 · Signal 61 … │
│                                          │ ── Facts & features ──             │
│                                          │ ── Rent history ──                 │
│                                          │ ── Nearby ──                       │
│                                          │ [Contact agent]                    │
└──────────────────────────────────────────┴───────────────────────────────────┘
```

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| UI-1 **[v2.1]** | Two-column layout: **left** = interactive lunar map; **right** = results card list (RES-1), replaced by the selected plot's listing when a plot is selected, with "← Back to results." | P0 | D |
| UI-2 | A recognizable Zillow parody following §0.1, without Zillow's name, logo, colors or assets in the product branding. | P0 | I |
| UI-3 **[v2.1]** | The fictional-premise disclaimer (wording in "At a glance") appears as fine print under every Moonstimate (ⓘ tooltip), in the footer, and once as a dismissible notice on first load. | P0 | I |
| UI-4 | Responsive down to 1280 px laptop width. Mobile is not required. | P1 | D |
| UI-6 **[v2.1]** | **Buy / Rent** tabs in the header. Buy shows Moonstimate pins and prices. Rent shows Rent Moonstimate pins and prices and reveals the Move-in and Stay controls (§5.6). | P1 | D |

*(v2.0's UI-5 "featured listings in the empty panel" is now RES-4.)*

### 5.2 Map

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| MAP-1 | Global lunar basemap (Moon Trek imagery or LOLA hillshade) with pan and zoom. A static fallback image is available offline. | P0 | D |
| MAP-2 **[v2.1]** | **Zillow marker behavior:** at low zoom, plots appear as small dots (colored by price band); at plot-level zoom, as price pills ("$4.2M"). Dense areas aggregate. | P0 | D |
| MAP-3 | Hovering a marker highlights the plot boundary *and its card in the results list*; clicking selects it and opens the listing. The selection persists while overlays and filters change. | P0 | D |
| MAP-4 | A South Pole District view in polar stereographic projection, reachable with one click (tab or inset). | P0 | D |
| MAP-5 **[v2.1]** | Plots that fail the landing-safety gate are shown as **grey "Off market" dots**, not price pills, with an "Off market: not safe to land" label on hover. Distinguished by shape and label, not color alone. | P0 | D |
| MAP-6 | A landmark label layer (named craters, Apollo/Luna/Chang'e landing sites, NASA's Artemis III candidate regions), toggleable. | P1 | D |
| MAP-7 | Search box that jumps to a named feature (e.g. "Shackleton," "Tranquility Base"). | P2 | D |

### 5.3 Listing

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| DET-1 | Plot name or ID, nearest named feature, center lat/lon, tier label ("Moon-wide estimate" or "Detailed survey"). | P0 | D |
| DET-2 **[v2.1]** | Moonstimate price (Rent Moonstimate on the Rent tab), a one-line why ("Priced high for near-constant sunlight and Earth views"), and the **Moonstimate range** (PRICE-3, P1). | P0 / P1 range | D |
| DET-10 **[v2.1]** | **Facts line** directly under the price, in Zillow's "bd · ba · sqft" position: `sunlit % · Earth contact % · mean slope ° · plot area km²`. Also shown on every results card. | P0 | D |
| DET-3 **[v2.1]** | Viability Score (0–100) plus **named scores** in the Walk Score style, each 0–100 with a one-line meaning: **Landing Score** (safety), **Sun Score** (power), **Signal Score** (comms), **Comfort Score** (thermal), **Views Score** (landmarks), **Ice Score** (polar only). | P0 | D |
| DET-4 | Facts & features in everyday units: sunlight % of year; longest night; Earth contact %; longest blackout; temperature min/mean/max (°C, K in tooltip); mean and P90 slope; buildable area %; landing-safe flag; land type; ice nearby (polar); solar energy per day. | P0 | D |
| DET-5 **[v2.1]** | **3D Tour** (polar plots): a tab next to "Photos" in the listing gallery. It shows a 360° horizon panorama of the plot's terrain skyline with the Sun's and Earth's paths. Segments blocked by terrain look different. Shows **time until next sunset / Earthset** at the time-slider position. (Same feature as v2.0's "sky view," renamed and placed where Zillow puts tours.) | P0 | D |
| DET-6 | Listing blurb generated from thresholds, e.g. "Bright, south-facing rim lot with 24/7 Earth views. Cozy −230 °C basement (PSR) next door." | P1 | D |
| DET-7 **[v2.1]** | **Rent history** chart: the Rent Moonstimate for a 1-month stay starting each month of the analysis year, driven by that month's sunlight and comms. Replaces v2.0's monthly "price history," because the Buy price no longer varies by month (D-6). | P1 | D |
| DET-8 | Tooltips on every fact: plain-language explanation, then (P1) formula and data source. | P0 / P1 | I |
| DET-9 | Nearby landmarks within N km, with distances (Zillow's "nearby schools" slot). | P1 | D |
| DET-11 **[v2.1, v2.2]** | **Badges** on cards and listings, all computed from data (thresholds in config): **Hot property** (top 5% viability), **Earth view** (polar or limb plot with earth_visible_frac ≥ 0.95; not on the near side, where it's universal), **Peak of light** (land type), **Price cut** (Rent tab only: rent for the chosen stay ≥ 10% below `rent_avg_usd_month`, the 1-year-stay rent), **Off market** (not buildable). At most 2 shown per card. | P1 | T |
| DET-12 **[v2.1]** | **Contact agent** button that opens Ask the realtor (AI). | P2 | D |
| DET-13 **[v2.1]** | **Save ♡** a plot (local storage) and a "Saved" list. | P2 | D |
| DET-14 **[v2.1]** | **Est. payment** parody ("Est. $18,400/mo"), using a fixed fictional rate and term from config, labeled as a joke in the tooltip. | P2 | D |

### 5.4 Filters, Home type and sort

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| FIL-1 | Filter by price range (Buy or Rent price, depending on the tab). Plots outside the range are hidden or dimmed. | P0 | D |
| FIL-2 | Filter by land type (multi-select): Mare · Highlands · Crater floor · Crater rim · PSR · Peak of light · Far side. | P1 | D |
| FIL-3 | "Hide off-market plots" toggle (v2.0 "Buildable only"). | P1 | D |
| FIL-4 **[v2.1]** | **Home type** (Zillow's filter of the same name): Any (default) · Lander pad · Habitat · Solar farm · Ice depot. Choosing a type (a) **hides plots that fail that type's gates** (§6.8; **[v2.2]** checked over the type's reference stay at its best move-in date, and calibrated so each type returns results) and (b) **computes a match % per plot** from the type's weights. It **does not change any price** (D-6). (Replaces v2.0's "Shopping for" presets that re-priced the map.) | P1 | D |
| FIL-7 **[v2.1]** | **Sort** dropdown on the results list: Price (high to low) · Price (low to high) · Viability · Sun Score · Signal Score · **Best match** (only when a Home type is chosen; default sort in that case). | P1 | D |
| FIL-5 | "More" panel: minimum sunlight % and minimum Earth contact % sliders. | P2 | D |
| FIL-6 | Filter and sort state reflected in the URL. | P2 | T |

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
| OV-7 | Comm window | Binary, time-dependent | Earth visible / not visible at the slider time | P1 |
| OV-8 | Ice access (polar) | Gradient | Distance to nearest PSR | P1 |
| OV-11 **[v2.1]** | Solar power | Gradient | Mean incident energy, Wh/m²/day (restored from the planning notes; data from SOL-2) | P1 |

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| OV-9 | Perceptually uniform, colorblind-safe palettes (diverging for temperature). | P0 | I |
| OV-10 | Overlay opacity slider. | P1 | D |

### 5.6 Time, Rent and scenarios

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| TIME-1 | Time slider across the analysis window (default one year, [TBD: 2028]), with hourly data in the polar tier and at least 6-hourly in the Moon-wide tier. | P1 | D |
| TIME-2 | The comm-window overlay, the instantaneous sunlit/dark view, and the 3D Tour's Sun and Earth positions update with the slider. **The Buy price does not change** (D-6). | P1 | D |
| TIME-3 | Play/pause animation. | P2 | D |
| RENT-1 **[v2.1]** | On the **Rent** tab, the user picks a **move-in date** and a **stay length** (2 weeks · 1 month · 3 months · 1 year). Moving the time slider while on Rent sets the move-in date. | P1 | D |
| RENT-2 **[v2.1]** | The **Rent Moonstimate** for the selected plot is computed from that plot's stats over the chosen stay window (§6.8), shown as "/mo" and as total stay cost. | P1 | T |
| RENT-3 **[v2.1]** | When the move-in date changes, the listing highlights the change and the reason, e.g. "Rent ↓ 35%: moving in 2 weeks later puts you in a 5-day night." The Price cut badge (DET-11) applies. | P1 | D |
| RENT-4 **[v2.1]** | Rent pins for the **whole map** recompute for the chosen window. Until then, Rent-tab pins show each plot's yearly average rent. | P2 | D |
| SCN-2 **[v2.2]** | Relay upgrade: a "what if" renovation toggle that assumes a relay satellite. Earth-contact penalties are removed and a separate **"With relay: $X"** value appears beside the Moonstimate, with the change shown neutrally. **The Buy price itself never changes** (D-6). | P2 | D |

*(v2.0's SCN-1 "move-in date re-prices the plot" is replaced by RENT-1…4. **Why:** Zillow's Buy prices don't depend on your move-in date, but its rentals do have one. See C1.)*

### 5.7 Results list **[v2.1]**

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| RES-1 **[v2.2]** | The right column shows a scrollable, **virtualized** grid of **listing cards** for plots in the current map view that pass the filters, headed "Lunar real estate · N results." At most **[TBD, e.g. 200]** cards are rendered, in sort order, with "Showing 200 of N" when capped. | P0 | D |
| RES-2 | Each card shows a thumbnail (basemap crop), price, facts line (DET-10), plot name, up to 2 badges (DET-11), and tier label. | P0 (badges P1) | D |
| RES-3 | Hovering a card highlights its pin; clicking opens the listing (UI-1). The list updates as the map pans/zooms (debounced, ≤ 200 ms, NFR-2). | P0 | D |
| RES-4 | On first load, the top of the list shows **"Plots for you"**: 2–3 featured listings (e.g. a polar rim plot, a far-side bargain, an Apollo-adjacent plot). (Was v2.0 UI-5.) | P1 | D |

---

## 6. Functional requirements: data and scoring

All heavy computation happens offline in a re-runnable Python pipeline that outputs static files.

### 6.1 EPH: ephemeris

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| EPH-1 | Query JPL Horizons once per quantity for the analysis window: target `301` (Moon), observer `500@399` (geocenter), `QUANTITIES='14,15,19,20'` (sub-Earth point, sub-solar point, Sun range, Earth range), hourly. Cache the responses to disk and commit them. | P0 | I |
| EPH-2 | For any location, compute Sun and Earth elevation and azimuth from the sub-solar and sub-Earth points, using the local east-north-up frame. Earth parallax is included for the polar tier. | P0 | T |
| EPH-3 | Validation: compare with direct Horizons topocentric queries (`CENTER='coord@301'`, `QUANTITIES='4'`) at 3 or more sites (near side, limb, south pole) on 3 or more dates. Pass: ≤ 0.1° with parallax (polar method); ≤ 1° for the smooth Moon-wide method. | P0 | A |
| EPH-4 | Horizons use is polite: cached, no parallel hammering, back off on errors. | P0 | I |

### 6.2 GRID: plots

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| GRID-1 | Moon-wide grid: 1° × 1° plots (configurable). | P0 | I |
| GRID-2 | South Pole District grid: ≈ 1 km plots in polar stereographic, built from finer analysis cells (≈ 240 m [TBD]). | P0 | I |
| GRID-3 | Each plot has a stable ID, center lat/lon, boundary polygon, tier, area (km², for the facts line **[v2.1]**), and all computed attributes. | P0 | T |
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
| SAFE-1 | Safe-slope threshold configurable; default 8°. | P0 | I |
| SAFE-2 | `landing_safe = safe_area_frac ≥ 0.25` (configurable). Plots failing this are "Off market" (MAP-5). | P0 | T |
| SAFE-3 | `hazard_score` = normalized combination of P90 slope, roughness and relief. | P0 | T |
| SAFE-4 | The listing states that boulder-scale hazards are below the data resolution. | P0 | I |

### 6.4 HOR + SOL: System B, sunlight and solar power

**Irradiance:** `TSI = L_sun / (4π R²)`, with `L_sun = 3.828 × 10²⁶ W` and `R` = Sun–Moon distance. TSI varies between ~1320 and ~1412 W/m² over the year. (The planning notes call this "atmospheric pressure"; it is irradiance, and the Moon has no atmosphere.)

**Visibility:**
- Moon-wide: the Sun is up when `e_sun > 0` (smooth Moon).
- Polar: the Sun is up when it clears the terrain horizon in its direction. Use the visible fraction of the solar disk, because the disk is ~0.53° wide and at the pole the Sun skims the horizon.

**Flux:**
- Horizontal surface: `F = TSI · max(0, sin e_sun) · V`.
- Vertical Sun-tracking panel (the polar default): `F = TSI · V`.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| HOR-1 | Precompute each polar analysis cell's terrain horizon: elevation vs. azimuth in ≤ 2° steps, including lunar curvature and terrain out to [TBD, ≥ 50 km]. This also feeds the 3D Tour (DET-5). | P0 (polar) | T |
| HOR-2 | Cross-check one site's horizon against an independent profile (Moon Trek or Quickmap). | P1 | A |
| SOL-1 | Compute TSI from the Sun–Moon distance at each step. | P0 | T |
| SOL-2 | Per plot over the window: `sunlit_frac`, mean flux, `energy_wh_m2_per_day`, `longest_dark_hours`, `longest_light_hours`; plus a downsampled time series for charts **and for Rent windows (RENT-2) [v2.1]**. | P0 | T |
| SOL-3 | Reference array power `P = F · A · η` (default A = 10 m², η = 0.30). | P1 | T |
| SOL-4 | Fallback: if HOR slips, the polar tier uses the smooth-Moon model, labeled "simplified lighting." Accept this only as a last resort; it weakens the south-pole story. The 3D Tour then shows a flat horizon with the label. | — | I |

### 6.5 TEMP: System C, temperature

**T1 model (P0):**
- Day: `T_day = [(1 − A)·F(t) / (εσ)]^¼`, with `A ≈ 0.12`, `ε ≈ 0.95`, `σ = 5.67 × 10⁻⁸`.
- Night floor: ≈ 95–100 K (equatorial); ≈ 40 K in PSRs.
- At the pole, `F(t)` uses terrain-aware sunlight.

For reference, the 1D heat equation `∂/∂z(k ∂T/∂z) = ρc ∂T/∂t` uses z = depth, not latitude. It's a stretch goal.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| TEMP-1 | Per plot: temperature min, mean and max over the window, using T1. | P0 | T |
| TEMP-2 | `thermal_hazard_score` penalizes extreme cold and large swings; thresholds in config. | P0 | T |
| TEMP-3 | Tooltip explains the ~300 °C day/night swing (no atmosphere; long lunar day). | P1 | I |
| TEMP-4 | Cross-check polar T1 results against LRO Diviner polar temperatures for a few plots, and document the differences. | P1 | A |
| TEMP-5 | Heat-equation (T2) model. | P2 | T |

### 6.6 COMM: System D, Earth communication

**Assumption:** simple line of sight. Comms are available when Earth's center is above the cutoff, and, at the pole, above the terrain horizon. The DSN's three complexes (Goldstone, Madrid, Canberra) are treated as continuous coverage. Relay satellites are out of scope, except for the SCN-2 scenario.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| COMM-1 | Elevation cutoff configurable; default 5°. | P0 | I |
| COMM-2 | Per plot: `earth_visible_frac`, `longest_blackout_hours`, `mean_earth_elevation_deg`, `comms_score`. | P0 | T |
| COMM-3 | Per-timestep visibility for the comm-window overlay and Rent windows, at reduced resolution. | P1 | T |
| COMM-4 | Polar comms are terrain-aware (via HOR). | P0 (polar) | T |

### 6.7 LAND + ICE: land types, landmarks, ice

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| LAND-1 | Primary land type per plot from elevation, slope, latitude and lighting (e.g. `sunlit_frac ≈ 0` → PSR; very high sunlight near the pole → Peak of light; lon beyond ±90° → Far side). | P1 | T |
| LAND-2 | Landmarks from the IAU/USGS Gazetteer of Planetary Nomenclature, plus a curated list of Apollo/robotic landing sites and the nine Artemis III candidate regions (Peak near Cabeus B, Haworth, Malapert Massif, Mons Mouton Plateau, Mons Mouton, Nobile Rim 1, Nobile Rim 2, de Gerlache Rim 2, Slater Plain). | P1 | I |
| LAND-3 | `landmark_score` from proximity to notable features. | P1 | T |
| ICE-1 | Polar plots: PSRs derived from our own terrain-aware lighting (`sunlit_frac = 0` over the year); distance to the nearest PSR reported as "Ice access." | P1 | T |
| ICE-2 | Tooltip: PSRs may hold water ice, but it's not confirmed. | P1 | I |
| LAND-4 | Refine land type using the USGS Unified Geologic Map. | P2 | T |

### 6.8 VS + PRICE + RENT: viability, scores and prices

**Viability (0–100)**, unchanged from v2.0:

```
viability = 100 · Σ wᵢ·sᵢ / Σ wᵢ          (only if all gates pass)
s_safety   = 1 − hazard_score
s_power    = normalize(energy_wh_m2_per_day) · penalty(longest_dark_hours)
s_comms    = earth_visible_frac · penalty(longest_blackout_hours)
s_thermal  = 1 − thermal_hazard_score
s_landmark = landmark_score
s_ice      = proximity to PSR (polar only; weight 0 by default)
```

Default weights: Safety 0.30 · Power 0.25 · Comms 0.20 · Thermal 0.15 · Landmarks 0.10.

Gate: `landing_safe = false` → **Off market**; viability capped at [TBD, e.g. 10] and no price pill (MAP-5).

**Named scores [v2.1].** Each sub-score is displayed as `round(100 · sᵢ)` under a Zillow-style name. The math is unchanged; only the labels are new.

| Sub-score | Displayed as | One-line meaning (tooltip) |
|---|---|---|
| s_safety | **Landing Score** | How much flat, safe ground the plot has |
| s_power | **Sun Score** | How much solar energy you get, and how short the nights are |
| s_comms | **Signal Score** | How often you can talk to Earth, and how short the blackouts are |
| s_thermal | **Comfort Score** | How mild the temperature extremes are |
| s_landmark | **Views Score** | How close you are to famous lunar sights |
| s_ice | **Ice Score** | How close you are to possible water ice (polar) |

**Home types [v2.1]** (FIL-4). These replace v2.0's "Shopping for" presets. The same weights and gates are now used for **filtering and a match %**, not for pricing.

```
match_type = 100 · Σ w_type,i · sᵢ / Σ w_type,i     (only for plots that pass the type's gates)
```

| Home type | Weight changes vs. defaults | Reference stay **[v2.2]** | Gates (plots failing are hidden) |
|---|---|---|---|
| Any | Defaults (match = viability) | Full year | — |
| Lander pad | Safety ↑, Power ↑ | 14 days | Longest night ≤ [TBD, e.g. 48] h within the best 14-day window of the year |
| Habitat | Comms ↑, Thermal ↑ | 90 days | Longest blackout ≤ [TBD] h within the best 90-day window |
| Solar farm | Power ↑↑ | Full year | Buildable area ≥ [TBD] %; sunlit ≥ [TBD] % |
| Ice depot | Ice ↑↑, Power ↑ | Full year | Ice access ≤ [TBD, e.g. 10] km (polar only) |

**[v2.2] Calibration rule:** in M3, set each gate from the computed distributions so every Home type returns at least [TBD, e.g. 50] plots in the South Pole District (and the Moon-wide tier where the type applies). Gates evaluated over a stay use per-plot precomputed "best window" values (`best_window` in §10), so filtering stays a static lookup.

*(v2.0 names "First lander" and "Home base" become "Lander pad" and "Habitat" so they read as property types, the way Zillow's Home type options do.)*

**Moonstimate (Buy price)**, formula unchanged from v2.0, computed from **full analysis-year** stats:

```
price = BASE · exp(k · viability/100) · (1 + landmark_premium) · scarcity_multiplier
```

- BASE ≈ $50,000; k tuned so the top plots reach the low millions and the worst the low thousands.
- Premiums: e.g. +25% within 50 km of an Apollo site; +50% for Peak-of-light rim plots.
- Rounded to real-estate numbers ($1.25M, $340K).
- **[v2.2]** `scarcity_multiplier` uses a cutoff stored in config (`scarcity_viability_cutoff`, the viability of the top-N% plot, written by the pipeline), so the browser can apply the same price function for rent.

**Moonstimate range [v2.1]:**

```
range = [ price · (1 − u_tier), price · (1 + u_tier) ]
u_tier = 0.25 (Moon-wide), 0.10 (South Pole District)      (config)
```

P2: derive `u` per plot from LOLA height/slope error layers (`LDEM_*_ERR`, `LDSM_*_ERR`).

**Rent Moonstimate [v2.1]** (RENT-2):

```
viability_stay = viability formula using SOL/COMM/TEMP stats over [move_in, move_in + stay]
rent_per_month = RENT_RATIO · price(viability_stay)          RENT_RATIO default 0.006 (≈ a real-world price-to-rent ratio)
stay_total     = rent_per_month · stay_months
```

Rent is computed client-side for the selected plot from the per-plot time series (SOL-2, COMM-3). Safety and landmarks don't change within a stay; sunlight, comms and temperature do.

**[v2.2]** `rent_avg_usd_month` (shipped per plot) is defined as the 1-year-stay rent, i.e. `RENT_RATIO · Buy price`. It is the reference for the Price cut badge and the Rent pins until RENT-4.

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| VS-1 | Weights, normalization bounds, penalties, gates, home types and reference stays **[v2.2]**, badge thresholds **[v2.1]**, range widths **[v2.1]**, RENT_RATIO **[v2.1]** and the scarcity cutoff **[v2.2]** live in one config file. | P0 | I |
| VS-2 | Normalization uses fixed reference ranges, not ranges relative to what's on screen, so scores mean the same everywhere. | P0 | I |
| VS-3 | Breakdown shown in the listing as named scores (DET-3). | P0 | D |
| VS-4 **[v2.1: P1 → P2]** | Scores within ±2 are labeled tied. Tie-break order: (1) smaller change in rent across move-in dates; (2) larger safety margin; (3) plot ID. **Why moved:** users and judges never see it; time goes to visible items instead. | P2 | T |
| VS-5 | Sanity tests run automatically (see §9). | P0 | T |
| VS-6 | User-adjustable weights in the UI. | P2 | D |
| VS-7 **[v2.1]** | Home-type match % and gates computed per FIL-4 without changing any price. | P1 | T |
| PRICE-1 | Price is deterministic from plot attributes + config. No randomness, and **no dependence on UI state** (D-6). **[v2.1]** | P0 | T |
| PRICE-2 | One-line price explanation (DET-2). | P0 | D |
| PRICE-3 **[v2.1]** | Moonstimate range as defined above. | P1 | T |
| RENT-5 **[v2.1]** | Rent for a full-year stay equals `RENT_RATIO · Buy price` within rounding (consistency test). | P1 | T |

---

## 7. Data sources

| Source | Agency | Used for | Pri |
|---|---|---|---|
| JPL Horizons API (`https://ssd.jpl.nasa.gov/api/horizons.api`, [docs](https://ssd.jpl.nasa.gov/api.html)) | NASA/JPL | Sub-solar and sub-Earth points, Sun and Earth distances, validation queries | P0 |
| LOLA global DEM ([USGS `Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif`](https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif)) | NASA LRO / USGS | Moon-wide slope, roughness, relief, land type | P0 |
| LOLA south-polar products ([NASA GSFC PGDA](https://pgda.gsfc.nasa.gov/products/90), e.g. `LDEM_80S_*`, `LDSM_80S_*`) | NASA LRO | Polar terrain, horizons, slope; error layers for range (P2) | P0 |
| NASA Moon Trek ([Trek API](https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=moon), WMTS tiles) | NASA | Basemap imagery/hillshade (static fallback for offline); card thumbnails | P0 |
| IAU/USGS Gazetteer of Planetary Nomenclature | IAU / USGS | Landmark names and coordinates | P1 |
| NASA Artemis III candidate regions (Oct 2024 announcement) | NASA | Landmark layer | P1 |
| LRO Diviner polar temperatures ([data](https://www.diviner.ucla.edu/data)) | NASA LRO | Temperature cross-check | P1 |
| USGS Unified Geologic Map of the Moon | USGS | Land-type refinement | P2 |
| Thermal model paper ([ScienceDirect S009457652500517X](https://www.sciencedirect.com/science/article/abs/pii/S009457652500517X)) | — | Heat-equation reference | P2 |

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
| NFR-2 | Overlay toggle / filter / sort / results-list update | < 200 ms | P0 |
| NFR-3 | Time slider scrub (comm window, 3D Tour) | ≥ 15 fps | P1 |
| NFR-4 **[v2.2]** | Static payload, excluding basemap tiles | < 25 MB core; polar detail (including every plot's horizon for the 3D Tour) lazy-loaded by tile, < 60 MB total [TBD] | P0 |
| NFR-5 | Offline demo mode: runs fully from local files with a static basemap | Required | P0 |
| NFR-6 | Pipeline re-runnable end to end with one command, using cached API responses | Required | P0 |
| NFR-7 | Accessibility: colorblind-safe palettes; keyboard-focusable markers and cards; status not by color alone | Best effort | P1 |
| NFR-8 | Every displayed metric documents its units and source | Required | P0 |
| NFR-9 | Static hosting (GitHub Pages, Netlify or Vercel). The only exception is a tiny proxy if the P2 AI is built. | Required | P0 |
| NFR-10 **[v2.1]** | Rent recomputation for the selected plot when move-in or stay changes | < 200 ms | P1 |

---

## 9. Acceptance criteria (MVP)

**Experience**
- [ ] A first-time user selects a plot (from a pin or a card) and reads its price and three key facts within 30 seconds, unaided.
- [ ] **[v2.1]** Shown the app with no explanation, a first-time user identifies it as "like Zillow" (checked in the M7 novice test).
- [ ] The South Pole District opens in one click and the 3D Tour plays for a polar plot.
- [ ] The fictional-premise disclaimer is visible.
- [ ] **[v2.1]** Changing filters, Home type, sort or the time slider never changes a Buy price (automated UI test).
- [ ] The app runs from local static files with the network disabled.

**Science sanity checks** (automated where possible)
- [ ] Near-side plots show `earth_visible_frac ≈ 1.0`; far-side centers ≈ 0.0; limb and polar plots are intermediate.
- [ ] Equatorial plots: `sunlit_frac ≈ 0.5`; longest darkness ≈ 14–15 Earth days (~355 h).
- [ ] TSI stays within ~1320–1412 W/m² across the year.
- [ ] Equatorial T1: daytime max ≈ 390 K; night ≈ 95–100 K.
- [ ] Horizons validation passes (EPH-3).
- [ ] Polar: known permanently shadowed crater interiors (e.g. Shackleton's floor) show `sunlit_frac ≈ 0`; known well-lit rim and ridge areas rank in the top tier.
- [ ] Steep crater walls are shown "Off market."
- [ ] **[v2.1]** A 1-year Rent stay matches `RENT_RATIO · Buy price` (RENT-5).

---

## 10. Interfaces and data contracts

**Pipeline outputs:** `plots_global.json` and `plots_polar.json` (one entry per plot):

```json
{
  "id": "SP-0412", "tier": "polar", "lat": -89.4, "lon": 132.0, "bounds": [[...]],
  "area_km2": 1.0,
  "name": "Shackleton Rim · Plot 12", "land_type": "crater_rim",
  "price_usd": 4200000, "price_range_usd": [3800000, 4600000],
  "rent_avg_usd_month": 25200,
  "viability": 87, "off_market": false,
  "scores": {"safety":0.91,"power":0.95,"comms":0.61,"thermal":0.55,"landmark":0.9,"ice":0.8},
  "badges": ["hot_property", "peak_of_light"],
  "best_window": {"lander_14d": {"longest_night_h": 30, "start": "2028-03-02"}, "habitat_90d": {"longest_blackout_h": 120, "start": "2028-02-10"}},
  "facts": {"slope_mean_deg":4.2,"slope_p90_deg":9.8,"safe_area_frac":0.62,"landing_safe":true,
            "sunlit_frac":0.82,"energy_wh_m2_per_day":21500,"longest_dark_hours":110,
            "temp_min_k":70,"temp_mean_k":190,"temp_max_k":330,
            "earth_visible_frac":0.61,"longest_blackout_hours":260,"ice_km":3.1},
  "nearby": [{"name":"Shackleton","km":8.1}],
  "blurb": "Bright rim lot with near-constant sun…",
  "monthly": {"sunlit":[...],"earth":[...],"rent":[...]}
}
```

**[v2.1] changes to the v2.0 contract:**
- Added `area_km2`, `price_range_usd`, `rent_avg_usd_month`, `off_market` and `badges`.
- **[v2.2]** Added `best_window` (Home-type gates) and defined `rent_avg_usd_month` as the 1-year-stay rent.
- `monthly.price` was renamed to `monthly.rent` (C15).
- Home-type match % is computed client-side from `scores`, so it isn't stored.

**Other outputs:**
- Overlay rasters (PNG with a known ramp, or single-band data colored in the client).
- **[v2.2]** Polar horizons for **every** South Pole District plot (3D Tour), quantized (e.g. 180 azimuths × uint8 at 0.1° steps) and grouped into lazy-loaded tiles.
- **[v2.2]** Per-plot `best_window` values for Home-type gates (e.g. `{"lander_14d":{"longest_night_h":30,"start":"2028-03-02"}, "habitat_90d":{...}}`).
- Per-plot time series and comm-window bitsets (for the slider and Rent windows).
- Ephemeris table (subsampled) for the client-side 3D Tour and slider.

**Frontend:** reads only static files; no runtime API calls (except the P2 AI proxy).

**Recommended stack** (team to confirm):
- Pipeline: Python (numpy, rasterio/GDAL, requests, pandas).
- Frontend: React or plain TypeScript with Leaflet (custom coordinate systems) or MapLibre/deck.gl; Recharts or Chart.js for charts.
- Hosting: GitHub Pages, Netlify or Vercel.

---

## 11. Presentation and judging

Judges see a video of up to 30 seconds or a deck of up to 7 slides including the title, publicly hosted, plus the project page and possibly a live demo. They score on Impact, Creativity, Validity, Relevance and Presentation. The full script and slides are in `docs/presentation.md` (updated for v2.2), and the deck is the "Lunar Listings — Space Apps 2026" Slides artifact.

| Criterion | Evidence we show |
|---|---|
| Impact | Anyone can explore lunar landing science; it turns specialist data into something people want to click; education plus the emerging lunar economy |
| Creativity | A full Zillow parody (Moonstimate, Rent tab, 3D Tour, Sun/Signal Scores, badges, listing blurbs) **[v2.1]** |
| Validity | NASA Horizons + LOLA; terrain-aware polar lighting; Horizons validation; sanity checks; formulas shown; price ranges; fictional premise labeled |
| Relevance | Compare sites and dates; Sun and Earth vs. the horizon; power and direct-to-Earth comms; time to sunset/Earthset |
| Presentation | One story, strong visuals, a 30 s video plus a 7-slide deck |

| ID | Requirement | Pri | Ver |
|---|---|---|---|
| PRS-1 | A ≤ 30 s video (primary link) and a ≤ 7-slide deck, public links, English. | P0 | I |
| PRS-2 | Demo mode: featured plots and scenarios preloaded, offline. | P0 | D |
| PRS-3 | Presentation mode: larger text and markers, no dev controls, 1920×1080. | P1 | D |
| PRS-4 | The story uses real numbers from the app (prices, sunlight %, Rent before/after a move-in shift). | P0 | D |
| PRS-5 | The project page names the NASA datasets and how each is used. | P0 | I |
| PRS-6 | Backup recordings of every demo step. | P0 | I |
| PRS-7 | Screenshots or clips captured at every milestone into `docs/presentation/`. | P1 | I |

### Live demo script (~3 minutes) **[v2.1]**
1. Open on the global map and results list: "The UN is selling the Moon. Here's the listings site."
2. Sort by price low to high; click the cheapest far-side card: "Great price… 0% Earth on the facts line, two-week nights. Signal Score: 0."
3. Toggle the Earth contact overlay: the near side lights up and the far side goes dark.
4. Jump to the South Pole District and toggle Sunlight: peaks of light glow and PSRs are black.
5. Click a Shackleton rim pin: a multi-million Moonstimate with its range, the HOT PROPERTY badge, named scores and blurb. Open the **3D Tour**: the Sun skims the jagged horizon, with the time until sunset shown.
6. Switch to **Rent**, then shift the move-in date by 2 weeks: the rent drops, a Price cut badge appears, and the listing says why.
7. Close: "Every price is computed from NASA data, terrain-aware at the pole, and validated against JPL Horizons."

---

## 12. Roadmap (not built at the hackathon)

| Next | Vision |
|---|---|
| Ask the realtor (AI), user-adjustable weights, compare, share and save | Plan a lunar town: pad + solar farm + depot + homes + rover routes, evaluated together |
| More Home types: manufacturing, relay station, rover base, resort | Speculative infrastructure (mass drivers, manufacturing) |
| Rover routes and a "Commute Score" | Live data from new missions; other worlds (Mars) |
| Relay and fission-power "renovations" across the whole map; Earth phase and "best week to visit" | |
| North Pole District; effort-to-reach (Δv) estimate | |

---

## 13. Open questions (resolve in M0)

| # | Question | Suggested default |
|---|---|---|
| 1 | Public product name | "Lunar Listings" (alternatives: Moonstimate, Crater & Barrel Realty). No "Zillow" in branding. |
| 2 | Analysis year | 2028 (Artemis era) |
| 3 | Grid sizes | 1° global; ~1 km polar; ~240 m polar analysis cells |
| 4 | Polar core area | 85–90°S, extend if time allows |
| 5 | Comms cutoff | 5° |
| 6 | Price per plot or per km²? | Per plot (simpler to read; area shown on the facts line) |
| 7 | Home-type gate values; off-market cap; tie tolerance | Set in config at M0 |
| 8 | Frontend framework and map library | Team choice |
| 9 | Horizon search distance | ≥ 50 km |
| 10 **[v2.1]** | RENT_RATIO and stay-length options | 0.006/month; 2 wk · 1 mo · 3 mo · 1 yr |
| 11 **[v2.1]** | Badge thresholds | Hot property = top 5% viability; Earth view ≥ 0.95; Price cut ≥ 10% below average rent |
| 12 | ~~Where do docs live?~~ **Resolved in v2.2:** canonical docs are in `docs/` (see `docs/README.md`); `Lunar-Navigator-*.docx` moved to `Claude outputs/archive/`. | — |
| 13 **[v2.2]** | Reference stays and gate values per Home type; minimum results per type | Lander pad 14 d, Habitat 90 d, others full year; ≥ 50 polar results each; tune in M3 |
| 14 **[v2.2]** | Results-list cap | 200 cards |

---

## Appendix A: Glossary

| Term | Meaning |
|---|---|
| Moonstimate | Our parody estimate of a plot's Buy price (like a Zestimate), with a range |
| Rent Moonstimate | Our parody monthly rent for a specific stay window (like a Rent Zestimate) |
| Viability Score | Our combined 0–100 rating |
| Landing / Sun / Signal / Comfort / Views / Ice Score | Named 0–100 sub-scores (safety, power, comms, thermal, landmarks, ice), in the style of Walk Score |
| Home type | A use for the plot (Lander pad, Habitat, Solar farm, Ice depot); filters and ranks, never re-prices |
| Off market | A plot that fails the landing-safety gate |
| 3D Tour | 360° view of a plot's terrain horizon with Sun and Earth paths (was "sky view"; fallback name "360° Tour") |
| Plot | A grid cell users browse (1° Moon-wide; ~1 km at the pole) |
| South Pole District | The detailed, terrain-aware polar tier |
| Terrain horizon | The skyline seen from a spot; at the pole it decides sunlight and Earth contact |
| TSI | Total Solar Irradiance: solar power per m² at a given distance from the Sun |
| PSR | Permanently Shadowed Region: never sunlit; extremely cold; may hold water ice |
| Peak of (near-)eternal light | High polar terrain that's sunlit most of the year |
| Sub-solar / sub-Earth point | The point on the Moon directly beneath the Sun / Earth |
| Libration | The Moon's apparent wobble, which makes Earth visibility intermittent near the limb and poles |
| DSN | NASA Deep Space Network |
| LOLA / LRO / Diviner | Lunar Orbiter Laser Altimeter / Lunar Reconnaissance Orbiter / LRO's thermal radiometer |

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
- Team sources: `Zillow on the moon planning.md`; earlier spec versions in `docs/archive/` (v0.4, v1.0, v2.0, v2.1); `Claude outputs/archive/Lunar-Navigator-*.docx` (superseded)
- Technical specification: `docs/technical-spec.md`
