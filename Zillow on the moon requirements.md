# Zillow on the Moon — Requirements Document

| | |
|---|---|
| **Status** | Draft v0.1 |
| **Last updated** | 2026-11-14 |
| **Source** | `Zillow on the moon planning.md` |
| **Working title** | Zillow on the Moon (public name TBD, see §12) |

---

## 1. Overview

### 1.1 Premise
A newly formed UN committee is governing the Moon and rapidly selling off plots of land for colonization. Our product is the real-estate marketplace for those plots: an interactive, Zillow-style map of the Moon where every region has a listing price derived from real scientific data.

### 1.2 Problem / Opportunity
Lunar science data (topography, illumination, thermal environment, Earth visibility) is public but locked behind APIs, GeoTIFFs, and papers that the general public will never open. Framing that data as a real-estate listing ("3 bd / 2 ba, great Earth views, minimal cliffs") turns it into something anyone can explore and compare.

### 1.3 Product Goal
Build an interactive lunar map that assigns property values to regions based on:
- Temperature range / average temperature
- Earth communication reliability
- Terrain and landing hazards
- Solar power potential
- Nearby landmarks and notable terrain features

…and lets users explore *why* a plot is priced the way it is through toggleable data overlays and a detail panel.

### 1.4 Goals
1. **Educate through play.** A user with no space background should understand, within a couple of minutes, why the lunar south pole is "prime real estate" and the far side is "cheap but off-grid."
2. **Be scientifically grounded.** Every price traces back to real data and a documented formula.
3. **Feel like Zillow.** Familiar layout and interactions so the parody lands instantly.
4. **Be demoable.** Loads fast, works without a backend at demo time, no live API dependency on stage.

### 1.5 Non-Goals
- Mission-grade landing-site certification.
- Real transactions, accounts, or payments.
- Trajectory/fuel-cost-to-site modeling (explicitly a stretch item, §6.6).
- Full-resolution (118 m) global analysis in the browser.

---

## 2. Target Users

| Persona | Description | What they need |
|---|---|---|
| **Curious public** | Interested in space, no technical background | Fun hook, plain-language explanations, no jargon walls |
| **Students** (HS / early undergrad) | Learning about the Moon, physics, or data science | Visible formulas and data sources, "learn more" links |
| **Space enthusiasts** | Follow Artemis, know some terms | Real site names, comparison of candidate regions, accurate overlays |
| **Hackathon judges** | Evaluating impact, use of NASA data, polish | Clear story, obvious NASA data use, working demo |

**Design principle:** every number shown must have a one-sentence plain-English explanation available on hover/click.

---

## 3. User Stories

| ID | As a… | I want to… | So that… | Priority |
|---|---|---|---|---|
| US-1 | visitor | see a map of the Moon covered in price tags | I immediately get the concept | P0 |
| US-2 | visitor | click a price tag and see that plot's details | I can understand what makes it valuable | P0 |
| US-3 | visitor | toggle a temperature/sunlight/comms overlay | I can see *why* some areas cost more | P0 |
| US-4 | visitor | filter by price range | I can find "affordable" or "luxury" plots | P0 |
| US-5 | visitor | filter by land type (mare, highlands, crater, polar…) | I can compare terrain types | P1 |
| US-6 | visitor | scrub a time slider and watch comm windows / lighting change | I understand the Moon's day/night and Earth visibility | P1 |
| US-7 | student | see the formula and data source behind each score | I can learn the underlying science | P1 |
| US-8 | visitor | see nearby landmarks (Apollo sites, famous craters) | plots feel like real places | P1 |
| US-9 | enthusiast | adjust how much each factor matters to me | I can find *my* ideal plot | P2 |
| US-10 | visitor | compare two plots side by side | I can decide between options | P2 |
| US-11 | visitor | share a link to a specific plot | I can show friends | P2 |

Priority key: **P0** = required for demo, **P1** = strongly desired, **P2** = stretch.

---

## 4. Functional Requirements — UI

### 4.1 Layout (Zillow parody)

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Logo]  Search crater/region…   [Price ▾] [Land type ▾] [Overlays ▾] │
├───────────────────────────────────────────┬──────────────────────────┤
│                                           │  ┌────────────────────┐  │
│        LUNAR MAP (pan / zoom)             │  │  plot imagery      │  │
│                                           │  └────────────────────┘  │
│     [$1.2M]        [$340K]                │  $4,200,000  Moonstimate │
│            [$8.9M]       [$75K]           │  Shackleton Rim, Plot 12 │
│                                           │  ★ Viability 87/100      │
│   ┌ overlay legend ┐                      │  ── Facts & features ──  │
│   │ ▓▓▓▒▒░░  temp  │                      │  Sunlight: 82% of year   │
│   └────────────────┘                      │  Earth contact: 61%      │
│  ◀━━━━━━━━●━━━━━━━━▶  time slider         │  Temp: -173°C … 54°C     │
│                                           │  Slope: 4.2° (safe)      │
│                                           │  Nearby: Shackleton crater│
└───────────────────────────────────────────┴──────────────────────────┘
```

| ID | Requirement | Priority |
|---|---|---|
| UI-1 | Two-column layout: **left** = interactive lunar map, **right** = detail panel for the selected plot. | P0 |
| UI-2 | Visual style is a recognizable parody of Zillow (price-pill markers, listing card, "Facts & features" section, estimate badge) **without** using Zillow's logo, name in the product branding, or proprietary assets. | P0 |
| UI-3 | Responsive down to laptop width (1280 px). Mobile is not required. | P1 |
| UI-4 | Empty state for the right panel invites the user to click a plot and highlights 2–3 "featured listings." | P1 |

### 4.2 Map

| ID | Requirement | Priority |
|---|---|---|
| MAP-1 | Display a global lunar basemap (LRO imagery or LOLA hillshade) with pan and zoom. | P0 |
| MAP-2 | Divide the surface into **plots** (grid cells — see §5.1) and render a clickable **price marker** for each plot visible at the current zoom. | P0 |
| MAP-3 | Marker density adapts to zoom (cluster or aggregate at low zoom to avoid clutter; show individual plots when zoomed in). | P0 |
| MAP-4 | Hovering a marker highlights its plot boundary; clicking selects it and populates the detail panel. | P0 |
| MAP-5 | Selected plot remains highlighted while overlays/filters change. | P0 |
| MAP-6 | Support a south-polar view (polar stereographic or a dedicated inset), since the most interesting real estate is near the pole and equirectangular projection distorts it badly. | P1 |
| MAP-7 | Landmark labels (named craters, Apollo/Luna/Chang'e landing sites, Artemis candidate regions) toggleable as a layer. | P1 |
| MAP-8 | Search box that jumps to a named feature (e.g., "Shackleton", "Tranquility Base"). | P2 |

### 4.3 Detail Panel (Listing)

| ID | Requirement | Priority |
|---|---|---|
| DET-1 | Show plot name/ID, center coordinates (lat/lon), and listing price. | P0 |
| DET-2 | Show the **Viability Score** (0–100) with a breakdown bar per factor. | P0 |
| DET-3 | "Facts & features" section with, at minimum: avg/min/max temperature, % time sunlit, longest darkness period, % time in Earth contact, longest comms blackout, mean slope, roughness, landing-safe flag, land type. | P0 |
| DET-4 | Each fact has an info tooltip with a plain-language explanation and (P1) the formula + data source. | P1 |
| DET-5 | "Nearby" list of landmarks within N km with distance. | P1 |
| DET-6 | Small time-series chart(s) for the selected plot over the analysis window (e.g., sunlit vs. dark, Earth elevation). | P1 |
| DET-7 | Humorous listing copy generated from the data (e.g., "Bright, south-facing rim lot with 24/7 Earth views. Cozy −230 °C basement (PSR)."). Templates driven by thresholds, not hand-written per plot. | P1 |
| DET-8 | "Price history" parody chart (fake but driven by e.g. illumination over the year). | P2 |

### 4.4 Filters

| ID | Requirement | Priority |
|---|---|---|
| FIL-1 | Filter by price range (min/max). Plots outside range are hidden or dimmed. | P0 |
| FIL-2 | Filter by land type (multi-select): Mare, Highlands, Crater floor, Crater rim, Permanently Shadowed Region (PSR), Peak of near-eternal light, Far side. | P1 |
| FIL-3 | "Landing-safe only" toggle. | P1 |
| FIL-4 | "Must have Earth contact ≥ X%" and "Must have sunlight ≥ X%" sliders. | P2 |
| FIL-5 | Filter state reflected in the URL. | P2 |

### 4.5 Overlays

Each overlay is a semi-transparent raster drawn over the basemap with a legend. Only one gradient overlay is active at a time (P0); blending/multiple is P2.

| ID | Overlay | Type | Value shown | Priority |
|---|---|---|---|---|
| OV-1 | Temperature | Gradient | Mean surface temp over window (toggle: mean / min / max) | P0 |
| OV-2 | Solar Power Potential | Gradient | Mean incident solar energy (Wh/m²/day) or % time sunlit | P0 |
| OV-3 | Communication Strength | Gradient | % of time Earth is above the elevation cutoff | P0 |
| OV-4 | Lighting Characteristics | Gradient | Longest continuous darkness (hours) | P1 |
| OV-5 | Terrain Hazards | Gradient | Slope (°) with hazard threshold highlighted | P0 |
| OV-6 | Viability Score | Gradient | Composite score 0–100 | P0 |
| OV-7 | Communication Window | **Binary**, time-dependent | Earth visible / not visible at the time-slider's current timestamp | P1 |

| ID | Requirement | Priority |
|---|---|---|
| OV-8 | Each overlay has a legend with units and a one-line explanation. | P0 |
| OV-9 | Overlay opacity slider. | P1 |
| OV-10 | Color scales are perceptually uniform and colorblind-safe (e.g., viridis/cividis; diverging scale for temperature). | P1 |

### 4.6 Time Controls

| ID | Requirement | Priority |
|---|---|---|
| TIME-1 | A time slider covering the analysis window (default: one Earth year, hourly or 6-hourly steps). | P1 |
| TIME-2 | Time-dependent layers (OV-7 comm window, instantaneous sunlit/dark) update when the slider moves. | P1 |
| TIME-3 | Play/pause animation. | P2 |
| TIME-4 | User-selectable "mission window" (start/end) that re-aggregates stats for the selected plot. | P2 |

---

## 5. Functional Requirements — Data & Scoring Systems

All heavy computation happens **offline in a preprocessing pipeline** that outputs static files consumed by the frontend (see §7). The browser never calls Horizons or downloads the full DEM.

### 5.1 Spatial Grid ("plots")

| ID | Requirement | Priority |
|---|---|---|
| GRID-1 | Define a global grid of plots. Recommended starting resolution: **1° × 1°** globally (~65k cells, ~30 km at the equator) for prices/overlays. | P0 |
| GRID-2 | A higher-resolution grid for the **south polar region** (e.g., poleward of −80°, ~1–5 km cells in polar stereographic) where terrain and lighting vary sharply. | P1 |
| GRID-3 | Each plot has a stable ID, center lat/lon, boundary polygon, and all computed attributes. | P0 |
| GRID-4 | Grid resolution is a single config value so it can be traded off against compute time. | P0 |

### 5.2 System A — Physical Landing-Site Safety

**Purpose:** Determine whether it is physically feasible to land in a plot: slope, surface roughness, and nearby hazards (cliffs, chasms, steep crater walls, mountains).

**Inputs:** LOLA DEM (USGS `Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif`), downsampled.

**Method:**
1. Downsample/resample the DEM to a working resolution (e.g., ~500 m–1 km globally; native resolution for the polar subset if time allows).
2. Compute **slope** per pixel from the elevation gradient (accounting for meters-per-degree shrinking with latitude):
   `slope = atan( sqrt( (dz/dx)² + (dz/dy)² ) )`
3. Compute **roughness** as the standard deviation of elevation (or of slope) in a moving window.
4. Compute **relief** (max − min elevation within the plot) as a proxy for cliffs/mountains/chasms.
5. Aggregate per plot: mean slope, P90 slope, fraction of area below the safe-slope threshold, roughness, relief.

**Outputs per plot:** `slope_mean_deg`, `slope_p90_deg`, `safe_area_frac`, `roughness_m`, `relief_m`, `landing_safe` (bool), `hazard_score` (0–1).

| ID | Requirement | Priority |
|---|---|---|
| SAFE-1 | Safe-slope threshold is configurable; default **8°** (typical lander tolerance; tighten to 5° as an option). | P0 |
| SAFE-2 | `landing_safe = safe_area_frac ≥ 0.25` (configurable) — i.e., enough flat ground exists somewhere in the plot. | P0 |
| SAFE-3 | `hazard_score` is a normalized combination of P90 slope, roughness, and relief. | P0 |

### 5.3 System B — Solar Power Generation Potential

**Purpose:** Estimate how much solar energy is available at each plot over time, how long it is in sunlight, and how long the dark periods last.

**Inputs:** JPL Horizons ephemerides (Sun position relative to the Moon; Sun–Moon distance), DEM (stretch: horizon shadowing).

**Equation (from planning notes) — Total Solar Irradiance as a function of distance:**

```
TSI = L_sun / (4π R²)     [W/m²]
L_sun = 3.828 × 10²⁶ W
R     = Sun–Moon distance [m]
```

TSI at the Moon varies between roughly **1320 and 1412 W/m²** over the year as the Earth–Moon system's distance from the Sun changes. (Note: the planning doc labels this "atmospheric pressure" — it is irradiance; the Moon has no atmosphere to attenuate it.)

**Incident flux on a horizontal surface at a site:**

```
F(t) = TSI(t) · max(0, sin(e_sun(t))) · V(t)
e_sun = solar elevation angle at the site
V     = 1 if sun is above the local terrain horizon, else 0   (MVP: V = 1 when e_sun > 0)
```

For a sun-tracking or vertical polar panel, use `TSI · V(t)` (no cosine loss) — expose as a toggle since polar landers typically use vertical arrays.

**Efficient computation for the whole grid:** rather than one Horizons query per plot, query Horizons **once** for the **sub-solar point** on the Moon over time (target `301`, observer `500@399` or similar, `QUANTITIES='15'` — Sun sub-longitude/sub-latitude), plus Sun range (`QUANTITIES='19'` or `VECTORS`). Then for each plot:

```
cos(ψ) = sin φ·sin φ_ss + cos φ·cos φ_ss·cos(λ − λ_ss)
e_sun  = 90° − ψ
```

where (φ, λ) is the plot center and (φ_ss, λ_ss) is the sub-solar point.

**Outputs per plot:** `sunlit_frac`, `mean_flux_w_m2`, `energy_wh_m2_per_day`, `longest_dark_hours`, `longest_light_hours`, time series (downsampled) for the detail chart.

| ID | Requirement | Priority |
|---|---|---|
| SOL-1 | Compute TSI from Sun–Moon distance at each timestep. | P0 |
| SOL-2 | Compute sunlit fraction and mean incident energy per plot over the analysis window (default 1 year). | P0 |
| SOL-3 | Compute longest continuous darkness period per plot. | P0 |
| SOL-4 | Estimate generated power for a reference array: `P = F · A · η` with configurable area `A` (default 10 m²) and efficiency `η` (default 0.30). | P1 |
| SOL-5 | Terrain horizon masking using the DEM (critical at the poles, where crater rims cause permanent shadow and ridges get near-continuous light). | P2 |

### 5.4 System C — Surface Temperature & Thermal Hazards

**Purpose:** Estimate on-site temperature conditions over time and flag thermal hazards (extreme cold in PSRs, extreme day/night swings).

**Reference model (from planning notes)** — 1D heat conduction into the regolith ([ScienceDirect S009457652500517X](https://www.sciencedirect.com/science/article/abs/pii/S009457652500517X)):

```
∂/∂z ( k(T,z) · ∂T(t,z)/∂z ) = ρ(z) · c(T) · ∂T(t,z)/∂t
T = temperature, t = time, z = depth below surface,
k = thermal conductivity, ρ = density, c = heat capacity
```

(Note: in this equation `z` is **depth**, not latitude; latitude enters through the surface boundary condition via solar flux.)

**Tiered approach:**

| Tier | Method | Priority |
|---|---|---|
| T1 (MVP) | **Radiative equilibrium** surface temperature during the day, fixed night floor:<br>`T_day = [ (1 − A) · F(t) / (ε σ) ]^¼`, with albedo `A ≈ 0.12`, emissivity `ε ≈ 0.95`, `σ = 5.67×10⁻⁸`.<br>Night: `T_night ≈ 95–100 K` (equatorial); PSR/near-pole dark: `≈ 40 K`. | P0 |
| T2 | Explicit finite-difference solution of the 1D heat equation above per plot (or per latitude band + flux history), with surface boundary `εσT⁴ = (1 − A)F(t) + k ∂T/∂z`. Use published regolith profiles for `k(T,z)`, `ρ(z)`, `c(T)`. | P2 |
| Alt | Use precomputed **LRO Diviner** temperature products instead of modeling, if they can be obtained and regridded in time. | P2 |

**Outputs per plot:** `temp_mean_k`, `temp_min_k`, `temp_max_k`, `temp_swing_k`, `thermal_hazard_score` (0–1). Display in °C with K in tooltip.

| ID | Requirement | Priority |
|---|---|---|
| TEMP-1 | Compute min/mean/max surface temperature per plot over the window using T1. | P0 |
| TEMP-2 | `thermal_hazard_score` penalizes extreme cold and large swings; define thresholds in config. | P0 |
| TEMP-3 | Tooltip explains why the Moon swings ~300 °C between day and night (no atmosphere, ~29.5-day day). | P1 |

### 5.5 System D — Earth Communication Windows

**Purpose:** Determine when each plot has direct line-of-sight to Earth, and minimize time without comms.

**Assumption:** Simple LOS model — if Earth is above the site's elevation cutoff, comms are available. The NASA Deep Space Network's three complexes (Goldstone, Madrid, Canberra) are ~120° apart in longitude, so Earth-side coverage is treated as continuous whenever the Moon is above Earth's horizon for at least one complex. Relay satellites are out of scope.

**Single-site query (from planning notes, south pole):**

```
COMMAND='399'  EPHEM_TYPE='OBSERVER'  CENTER='coord@301'  COORD_TYPE='GEODETIC'
SITE_COORD='0,-89.9,0'  QUANTITIES='4'  ELEV_CUT='<elevation cut>'
START_TIME='<start>'  STOP_TIME='<stop>'  STEP_SIZE='1h'
```

`<elevation cut>` = antenna elevation limit in degrees; site is in contact when Earth's elevation > cutoff.

**Efficient computation for the whole grid:** query the **sub-Earth point** on the Moon once (target `301`, observer `500@399`, `QUANTITIES='14'` — observer sub-longitude/sub-latitude) and compute Earth elevation per plot with the same spherical formula as §5.3. Libration makes the sub-Earth point wander ~±7–8°, which is exactly what creates intermittent comms near the limb and the poles. Validate against the single-site `QUANTITIES='4'` query at 3–5 reference sites (parallax and terrain cause small differences).

**Outputs per plot:** `earth_visible_frac`, `longest_blackout_hours`, `mean_earth_elevation_deg`, per-timestep binary visibility (for OV-7), `comms_score` (0–1).

| ID | Requirement | Priority |
|---|---|---|
| COMM-1 | Default elevation cutoff configurable; default **5°**. | P0 |
| COMM-2 | Compute visibility fraction and longest blackout per plot over the window. | P0 |
| COMM-3 | Provide per-timestep visibility for the time-slider binary overlay (may be stored at coarser resolution/time step to keep file sizes small). | P1 |
| COMM-4 | Validate grid method against direct Horizons site queries for at least 3 sites (near side, limb, south pole). | P1 |
| COMM-5 | Terrain masking of Earth (local horizon from DEM). | P2 |

### 5.6 System E — Effort to Reach Site (Stretch)

Fuel/Δv and launch-window feasibility to reach a site from Earth. **Explicitly out of scope for the hackathon** per planning notes ("VERY FAR OFF"). If attempted, a crude proxy is acceptable (e.g., small penalty for high-latitude/polar sites and far side). Priority **P2**.

### 5.7 Land Type & Landmarks

| ID | Requirement | Priority |
|---|---|---|
| LAND-1 | Assign each plot a primary land type. MVP: derive from elevation + slope + latitude + illumination (e.g., low/flat near side → Mare; high/rough → Highlands; `sunlit_frac ≈ 0` → PSR; `sunlit_frac` very high near pole → Peak of light; lon beyond ±90° → Far side). | P1 |
| LAND-2 | Optionally refine using the USGS Unified Geologic Map of the Moon. | P2 |
| LAND-3 | Load named landmarks (craters, maria, montes, landing sites) from the IAU/USGS Gazetteer of Planetary Nomenclature, plus a hand-curated list of Apollo/robotic landing sites and Artemis candidate regions. | P1 |
| LAND-4 | Compute `landmark_score` from proximity to notable features (closer/more famous = higher). | P1 |

### 5.8 Viability Score (Evaluation Function)

Composite score in [0, 100] from normalized sub-scores (each in [0, 1], higher = better):

```
viability = 100 · Σ wᵢ · sᵢ / Σ wᵢ

s_safety   = 1 − hazard_score            (hard 0 if !landing_safe, configurable)
s_power    = normalize(energy_wh_m2_per_day) · penalty(longest_dark_hours)
s_thermal  = 1 − thermal_hazard_score
s_comms    = earth_visible_frac · penalty(longest_blackout_hours)
s_landmark = landmark_score
```

| Factor | Default weight |
|---|---|
| Safety | 0.30 |
| Power | 0.25 |
| Comms | 0.20 |
| Thermal | 0.15 |
| Landmarks / "views" | 0.10 |

| ID | Requirement | Priority |
|---|---|---|
| VS-1 | Weights and normalization bounds live in one config file. | P0 |
| VS-2 | Score breakdown is shown in the detail panel (DET-2). | P0 |
| VS-3 | User-adjustable weights in the UI re-rank plots client-side (requires sub-scores shipped to the client). | P2 |

### 5.9 Pricing Model ("Moonstimate")

Price is a monotonic, playful function of viability with a few premiums so the map has a believable spread:

```
price = BASE · exp(k · viability/100) · (1 + landmark_premium) · scarcity_multiplier
```

- `BASE` ≈ $50,000, `k` tuned so the top plots land in the low millions and the worst in the low thousands.
- `landmark_premium`: e.g., +25% within 50 km of an Apollo site, +50% for "Peak of light" rim plots.
- `scarcity_multiplier`: optional boost for plots in the top N% (polar rims) — keeps the south pole the "Manhattan of the Moon."
- Round to "real-estate" numbers ($1.25M, $340K).

| ID | Requirement | Priority |
|---|---|---|
| PRICE-1 | Price is deterministic from plot attributes + config (no randomness), so it's reproducible and explainable. | P0 |
| PRICE-2 | Detail panel explains the price in one line ("Priced high for near-constant sunlight and Earth views"). | P1 |

---

## 6. Data Sources

| Source | Used for | Access | Notes |
|---|---|---|---|
| **JPL Horizons API** — `https://ssd.jpl.nasa.gov/api/horizons.api` ([docs](https://ssd.jpl.nasa.gov/api.html)) | Sun–Moon / Earth–Moon geometry, sub-solar & sub-Earth points, site-specific Earth elevation | REST, text/JSON | Destinations: `10` Sun, `301` Moon, `399` Earth. Vectors query from notes: `EPHEM_TYPE='VECTORS'`, `CENTER='500@399'`, `VEC_TABLE='3'`, `OUT_UNITS='AU-D'`, `STEP_SIZE='1d'`; RG column = distance in AU. Cache all responses to disk. |
| **USGS LOLA DEM** — [`Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif`](https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif) | Elevation → slope, roughness, relief, land type | GeoTIFF download | Very large (multi-GB). Download once, downsample in preprocessing. Do not ship to client. |
| **NASA Moon Trek** — [Trek API](https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=moon) | Basemap imagery / hillshade tiles for the map | WMTS tiles | Primary basemap candidate; have a static fallback image for offline demo. |
| **IAU/USGS Gazetteer of Planetary Nomenclature** *(suggested)* | Landmark names & coordinates | CSV/shapefile download | For MAP-7, LAND-3, LAND-4. |
| **USGS Unified Geologic Map of the Moon** *(suggested, P2)* | Land type refinement | Shapefile | For LAND-2. |
| **LRO Diviner** *(suggested, P2)* | Measured surface temperatures | PDS products | Alternative to modeling (§5.4). |
| Thermal model paper ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S009457652500517X)) | Heat-equation reference & material properties | Paper | For T2 model. |

---

## 7. System Architecture

### 7.1 High-Level

```
┌────────────────────────── Offline pipeline (Python) ───────────────────────────┐
│                                                                                │
│  Horizons API ──► ephemeris cache (sub-solar pt, sub-Earth pt, Sun range)      │
│  LOLA DEM ─────► downsample ─► slope / roughness / relief rasters              │
│  Gazetteer ────► landmarks table                                               │
│                         │                                                      │
│                         ▼                                                      │
│      Systems A–D per plot ─► sub-scores ─► viability ─► price ─► land type     │
│                         │                                                      │
│                         ▼                                                      │
│      Outputs: plots.json / .geojson, overlay PNG tiles or rasters,             │
│               timeseries (per-plot, downsampled), comm-window bitsets          │
└────────────────────────────────────────────────────────────────────────────────┘
                          │  static files
                          ▼
┌──────────────────────── Frontend (static web app) ─────────────────────────────┐
│  Map lib (Leaflet / MapLibre / deck.gl) + basemap tiles                        │
│  Price markers, overlays, filters, time slider, detail panel, charts           │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Recommended Stack (suggestion — team to confirm)

| Layer | Recommendation | Why |
|---|---|---|
| Pipeline | Python: `numpy`, `rasterio`/`GDAL`, `requests`, `pandas`, optionally `xarray` | Standard for GeoTIFF + array math |
| Frontend | React or plain TS + **Leaflet** (simple, supports custom CRS) or **MapLibre/deck.gl** (better for large marker/raster layers) | Fast to build Zillow-like UI |
| Charts | Lightweight chart lib (e.g., Recharts, Chart.js) | Detail-panel time series |
| Hosting | Static hosting (GitHub Pages / Netlify / Vercel) | No backend needed at demo time |

### 7.3 Data Contracts (initial)

`plots.json` (one entry per plot):

```json
{
  "id": "SP-0412",
  "lat": -89.4, "lon": 132.0,
  "bounds": [[...]],
  "land_type": "crater_rim",
  "price_usd": 4200000,
  "viability": 87,
  "scores": { "safety": 0.91, "power": 0.95, "comms": 0.61, "thermal": 0.55, "landmark": 0.9 },
  "facts": {
    "slope_mean_deg": 4.2, "slope_p90_deg": 9.8, "landing_safe": true,
    "sunlit_frac": 0.82, "energy_wh_m2_per_day": 21500, "longest_dark_hours": 110,
    "temp_min_k": 70, "temp_mean_k": 190, "temp_max_k": 330,
    "earth_visible_frac": 0.61, "longest_blackout_hours": 260
  },
  "nearby": [{ "name": "Shackleton", "km": 8.1 }],
  "blurb": "Bright rim lot with near-constant sun..."
}
```

Overlays: one raster per overlay (PNG with a known color ramp, or single-band data the client colorizes). Comm windows: per-plot bitset per timestep at reduced spatial/temporal resolution.

---

## 8. Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | Initial load time on a laptop over decent Wi-Fi | < 3 s to interactive map |
| NFR-2 | Overlay toggle / filter response | < 200 ms |
| NFR-3 | Time slider scrub | ≥ 15 fps for OV-7 |
| NFR-4 | Total static payload (excluding basemap tiles) | < 25 MB |
| NFR-5 | **Offline demo mode**: the app runs fully from local files with a static basemap fallback | Required |
| NFR-6 | Pipeline is re-runnable end-to-end from a single command with cached API responses | Required |
| NFR-7 | Horizons usage is polite: cache responses, no parallel hammering, back off on errors | Required |
| NFR-8 | Accessibility: colorblind-safe palettes, keyboard-focusable markers, text alternatives for scores | Best effort |
| NFR-9 | Every displayed metric documents its units and source | Required |

---

## 9. MVP Scope & Milestones

### 9.1 MVP (must ship for demo)
- Global 1° grid with prices on an interactive basemap (MAP-1–5)
- Detail panel with viability breakdown and facts (DET-1–3)
- Price filter (FIL-1)
- Overlays: Temperature, Solar, Comms strength, Terrain hazards, Viability (OV-1,2,3,5,6)
- Systems A, B, C (T1), D using the sub-point grid method
- Static, offline-capable build

### 9.2 Suggested Build Order

| Phase | Work | Parallelizable by |
|---|---|---|
| 0. Setup | Repo structure, download DEM, verify Horizons queries, pick map lib, stub `plots.json` with fake data | Everyone |
| 1. Skeleton | Frontend renders basemap + fake markers + detail panel from stub JSON | Frontend |
| 1. Geometry | Ephemeris cache: sub-solar point, sub-Earth point, Sun range over 1 year | Data A |
| 1. Terrain | DEM downsample → slope/roughness/relief per plot | Data B |
| 2. Systems | Solar (B), thermal T1 (C), comms (D) per plot | Data A |
| 2. UI | Overlays, legends, filters, Zillow styling | Frontend |
| 3. Scoring | Viability + price + land type + landmarks + blurbs | Data B |
| 3. Integrate | Swap stub JSON for real pipeline output | All |
| 4. Polish | South polar view, time slider, tooltips/formulas, featured listings, demo script | All |

### 9.3 Demo Script (target ~3 min)
1. Open on the global map: "The UN is selling the Moon. Here's the listings site."
2. Click a cheap far-side plot → "Great price… zero Earth contact, two-week nights."
3. Toggle **Comms** overlay → near side lights up, far side goes dark.
4. Jump to the south pole → toggle **Solar** → peaks of light glow; PSRs are black.
5. Click a Shackleton rim plot → multi-million "Moonstimate," breakdown explains why.
6. Scrub the time slider → comm windows flicker on/off with libration.
7. Close: "Every price is computed from NASA data — here are the formulas."

---

## 10. Acceptance Criteria (MVP)

- [ ] A first-time user can select a plot and read its price and three key facts within 30 seconds, unaided.
- [ ] Near-side plots show `earth_visible_frac ≈ 1.0`; far-side center plots show `≈ 0.0`; limb/polar plots show intermediate values.
- [ ] Equatorial plots show `sunlit_frac ≈ 0.5` and longest darkness ≈ 14–15 Earth days (~355 h).
- [ ] Computed TSI stays within ~1320–1412 W/m² across the year.
- [ ] Equatorial daytime max temperature lands near ~390 K and night near ~95–100 K (T1 sanity check).
- [ ] Grid-method Earth elevation matches direct Horizons site queries within ~2° at the reference sites.
- [ ] South-polar rim plots rank in the top tier of viability/price; steep crater walls are flagged unsafe.
- [ ] App runs from local static files with network disabled.

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| DEM is multi-GB; slow to download/process | Blocks terrain system | Start download in phase 0; downsample early; consider a pre-downsampled product or Trek tiles as fallback |
| Horizons rate limits / downtime during hackathon | Blocks solar & comms | Use sub-point method (2–3 queries total, not one per plot); cache to disk and commit the cache |
| Equirectangular projection distorts poles where the best real estate is | Confusing UX | Dedicated polar stereographic inset (MAP-6) |
| Without terrain horizon masking, polar lighting is unrealistic (no true PSRs / peaks of light) | Weakens the south-pole story | Clearly label MVP as "smooth-Moon" model; prioritize SOL-5 for the polar subset only if time allows; optionally hand-annotate known PSRs/peaks from literature |
| Full heat-equation model is too slow/complex | Thermal system late | Ship T1 equilibrium model; T2 is stretch |
| Too many markers kills performance | Laggy map | Zoom-based aggregation; canvas/WebGL rendering |
| Parody too close to Zillow branding | IP concerns in public demo | Original name/logo/colors; parody the *layout*, not assets |
| Scope creep | Nothing finished | Hold the P0 line; fake-data stub lets UI and data proceed in parallel |

---

## 12. Open Questions

1. **Public product name?** (e.g., "Moonstimate", "Lunar Listings", "Crater & Barrel Realty") — avoid using "Zillow" in the shipped branding.
2. **Analysis window:** one calendar year starting when? A specific Artemis-relevant period?
3. **Grid resolution** vs. compute budget — confirm 1° global + finer polar is achievable.
4. **Single global map vs. south-pole-first?** The pole is the most scientifically interesting area; could lead the demo there.
5. **Elevation cutoff** for comms — confirm 5° default.
6. **Should prices be per plot or per km²?**
7. **Frontend framework** and map library choice.
8. Is there a target hackathon challenge statement the requirements should explicitly map to?

---

## 13. Glossary

| Term | Meaning |
|---|---|
| **DEM** | Digital Elevation Model — raster of surface heights |
| **LOLA** | Lunar Orbiter Laser Altimeter (on LRO); source of the DEM |
| **LRO** | Lunar Reconnaissance Orbiter |
| **TSI** | Total Solar Irradiance — solar power per m² at a given distance from the Sun |
| **PSR** | Permanently Shadowed Region — crater floors near the poles that never see sunlight; extremely cold, may hold water ice |
| **Peak of (near-)eternal light** | High polar terrain that is sunlit most of the year |
| **Sub-solar / sub-Earth point** | The point on the Moon directly beneath the Sun / Earth at a given time |
| **Libration** | Apparent wobble of the Moon as seen from Earth, letting ~59% of its surface be seen over time; causes intermittent Earth visibility near the limb |
| **DSN** | NASA Deep Space Network — Earth ground stations used for deep-space comms |
| **Elevation cutoff** | Minimum angle above the horizon at which an antenna can communicate |
| **Viability Score** | Our composite 0–100 rating of a plot |
| **Moonstimate** | Our parody price estimate |
