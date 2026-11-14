# Lunar Listings — Technical Specification

*NASA Space Apps Challenge 2026 · Team afc-spaceapps*

*Version 0.2 · 14 Nov 2026 · Decisions confirmed: React + deck.gl stack (D2), Earth contact = `terrain_margin` (T3). Task-level plan: `docs/build-plan.md`.*

*Implements `docs/requirements.md` **v2.2 (final)**. Requirement IDs (e.g. `HOR-1`, `RENT-2`) refer to that document. Build order: `docs/milestones.md`.*

---

## 0. Purpose, scope, conventions

This document says **how** to build what the requirements say. It fixes the architecture, repo layout, algorithms, data formats, interfaces between team tracks, and the test plan, so that the four tracks (Data A, Data B, Frontend, Presentation) can work in parallel from M0.

**Conventions**
- **Units:** SI internally (meters, seconds, kelvin, W/m²); degrees at interfaces where noted. Angles inside formulas are radians unless suffixed `_deg`.
- **Time:** UTC everywhere. The analysis year default is **2028** (a leap year: 366 days = **8,784 hourly steps**). Time index `t = 0 … 8783` is hours since `2028-01-01T00:00Z`.
- **Lunar radius:** `R = 1,737,400 m` (sphere; LOLA's reference radius). Heights are relative to this sphere.
- **Longitude:** east-positive, −180°…180°, in the Moon mean-Earth/polar-axis (ME) frame.
- **"Must / should"** follow the requirement priorities. Anything marked **[DECIDE]** is a choice for the team to confirm at M0. Default given.

---

## 1. Architecture

```
┌──────────────── pipeline/ (Python 3.11, offline) ────────────────┐      ┌────────── app/ (static web app) ──────────┐
│ fetch → ephemeris → terrain → horizons → visibility+stats        │      │ Vite + React + TypeScript                  │
│       → plots (aggregate) → land/ice/landmarks → scoring/price   │ ───▶ │ deck.gl map (two projections) · panels     │
│       → export (columnar bins + detail tiles + PNG overlays)     │ files│ Web Worker: rent, live visibility, filters │
│ validate (Horizons check, sanity tests)                          │      │ No runtime API calls (offline-capable)     │
└──────────────────────────────────────────────────────────────────┘      └────────────────────────────────────────────┘
                 config/lunar-listings.yaml  ── shared by both (exported as app/public/data/config.json)
```

### 1.1 Key decisions

| ID | Decision | Rationale | Alternative considered |
|---|---|---|---|
| **D1** | **All science precomputed offline in Python**; the app only reads static files. | Offline demo (NFR-5), static hosting (NFR-9), no Horizons calls on stage. | A backend API: not needed and adds a failure point. |
| **D2** ✅ confirmed | **Frontend: Vite + React + TypeScript, map rendered with deck.gl `OrthographicView` over pre-rendered basemap images**, one per projection (equirectangular Moon-wide; polar stereographic South Pole). | Works offline with no tile server. The same code path handles both projections, because we draw in projected meters. WebGL handles ~65k + ~90k markers (MAP-2). | Leaflet + Proj4Leaflet: simpler, but slower with tens of thousands of markers and awkward for two CRSs. MapLibre: needs vector/raster tiles in a web projection. Flutter (web + native): considered and rejected for this event. Flutter web has a heavier first load, no true background threads, and needs hand-batched drawing for ~150k markers; it's better if native mobile apps become a goal. |
| **D3** | **Columnar binary files for map-wide attributes, plus lazily loaded per-tile JSON details.** The logical per-plot record is still the one in requirements §10. | Per-plot JSON for ~155k plots would be ~90 MB. Columnar typed arrays keep the core under the 25 MB budget (NFR-4). | One big JSON: too large and slow to parse. |
| **D4** | **The browser recomputes time-dependent values** (instantaneous visibility, 3D Tour paths, Rent stats) from the shipped **ephemeris table + per-plot horizons**, in a Web Worker. | Avoids shipping per-plot hourly time series and bitsets (100+ MB). One plot × 8,784 hours is microseconds of work. | Shipping bitsets/time series: far too large. |
| **D5** | **One scoring/visibility implementation per language, held in parity by golden test vectors** (Python is the reference; TypeScript must match). | D4 means two implementations of the same formulas; golden files catch drift. | Compiling Python to WASM: too slow to set up in a hackathon. |
| **D6** | **One config file** `config/lunar-listings.yaml` for every tunable (weights, gates, thresholds, RENT_RATIO, grid sizes…); the pipeline also exports it to `config.json` for the app. | VS-1; the app and pipeline can't disagree. | Constants in code: drift and slow tuning. |
| **D7** | **Python numerics: NumPy + Numba** for the hot loops (horizons, visibility); rasterio/GDAL for rasters; SciPy for distance transforms. | Horizons and per-cell visibility are ~10¹⁰ simple operations: fine in Numba (seconds to minutes on a laptop), too slow in pure Python. | Pure NumPy vectorization: memory blow-up. C++: slower to write. |

---

## 2. Repository layout

```
afc-spaceapps/
├─ docs/                         # requirements, milestones, presentation, this spec
├─ config/
│  └─ lunar-listings.yaml        # D6: every tunable
├─ pipeline/                     # Python package (Data A + Data B)
│  ├─ pyproject.toml             # deps: numpy, numba, rasterio, scipy, pandas, requests, pyyaml, pytest
│  ├─ lunar_listings/
│  │  ├─ cli.py                  # `python -m lunar_listings <stage>`
│  │  ├─ config.py               # load + validate YAML, export config.json
│  │  ├─ fetch/                  # horizons.py, dem.py, gazetteer.py, artemis.py
│  │  ├─ ephemeris.py            # parse Horizons → unit vectors, distances
│  │  ├─ geometry.py             # ENU frames, az/el, parallax, projections   (shared formulas → golden vectors)
│  │  ├─ terrain.py              # DEM resample, slope/roughness/relief, safe fraction
│  │  ├─ horizons.py             # Numba ray-march terrain horizons
│  │  ├─ visibility.py           # Numba per-cell/hour sun & earth visibility, stats
│  │  ├─ thermal.py              # T1 model
│  │  ├─ plots.py                # grid definitions, cell→plot aggregation, best cell
│  │  ├─ land.py                 # land type, landmarks, ice/PSR distances
│  │  ├─ scoring.py              # sub-scores, viability, named scores, home types, best windows
│  │  ├─ pricing.py              # Moonstimate, range, rent, badges, blurbs
│  │  ├─ export.py               # columnar bins, detail tiles, horizons tiles, overlays, manifest
│  │  ├─ stub.py                 # M0: fake data with the real formats
│  │  └─ validate.py             # EPH-3 Horizons comparison, sanity report
│  └─ tests/                     # pytest; golden/ test vectors shared with app
├─ app/                          # Frontend
│  ├─ package.json               # vite, react, typescript, deck.gl, zustand, react-window, recharts, vitest, playwright
│  ├─ public/data/               # pipeline output (or stub) — see §5
│  └─ src/ …                     # see §6
├─ data/                         # gitignored: raw downloads, caches, intermediates
│  ├─ raw/  cache/  work/
├─ Makefile                      # one-command targets (§8)
└─ .github/workflows/ci.yml
```

---

## 3. Pipeline: algorithms

Run as stages (each stage caches its outputs in `data/work/` keyed by config hash):
`fetch → ephemeris → terrain → horizons → visibility → plots → land → score → export → validate`.

### 3.1 Fetch

**Horizons, sub-points and distances (EPH-1).** One request (or one per quarter if the response is large):

```
https://ssd.jpl.nasa.gov/api/horizons.api?format=text
  &COMMAND='301' &OBJ_DATA='NO' &MAKE_EPHEM='YES' &EPHEM_TYPE='OBSERVER'
  &CENTER='500@399' &START_TIME='2028-01-01' &STOP_TIME='2029-01-01' &STEP_SIZE='1h'
  &QUANTITIES='14,15,19,20' &ANG_FORMAT='DEG' &CSV_FORMAT='YES' &RANGE_UNITS='KM'
```

- Quantity 14 gives the **sub-Earth point** (observer sub-lon/lat), 15 the **sub-solar point**, 19 the Sun–Moon range `r`, and 20 the Earth–Moon range `delta`.
- Horizons states whether longitudes are east- or west-positive **at the end of the output**. The parser must read that line and convert to east-positive, or fail loudly.
- Cache the raw text in `data/cache/horizons/` and **commit the parsed CSV** (`pipeline/data/ephemeris_2028.csv`, ~1 MB). The pipeline runs without network after that (NFR-6).
- Be polite: no parallel requests; retry with backoff (EPH-4).

**Horizons, validation (EPH-3).** For each validation site and target `10` (Sun) and `399` (Earth):
`CENTER='coord@301' COORD_TYPE='GEODETIC' SITE_COORD='<lon_E>,<lat>,<alt_km>' QUANTITIES='4'`, a few dates at 1 h steps. The output is apparent azimuth and elevation with no refraction at non-Earth sites.

**DEMs.**

| Product | Source | Use |
|---|---|---|
| `Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif` | USGS | Moon-wide terrain, resampled |
| `LDEM_80S_80MPP_ADJ.TIF` | NASA GSFC PGDA | Polar far field for horizons; polar basemap hillshade |
| `LDEM_80S_20MPP_ADJ.TIF` cropped to the core area | NASA GSFC PGDA | Polar near field for horizons; slopes |
| `LDSM_80S_20MPP_ADJ.TIF` (slope) + `_ERR` layers | NASA GSFC PGDA | Safe-area fraction; P2 ranges |
| `LDEM_80S_80MPP_ADJ_HILL.TIF` | NASA GSFC PGDA | Polar basemap image |

Store SHA-256 in `pipeline/data/sources.yaml`; `make fetch` verifies them. **Read every CRS and transform from the GeoTIFF headers.** Never hard-code the projection; the PGDA products are south polar stereographic in meters.

**Gazetteer and Artemis regions.** IAU/USGS nomenclature CSV (craters, montes, landing sites) → `pipeline/data/landmarks.csv`. The 9 Artemis III regions and the Apollo/robotic landing sites are hand-curated with source links.

### 3.2 Ephemeris → vectors

For each hour `t`:
- `ŝ(t)` = unit vector to the Sun in the Moon-fixed frame, from the sub-solar lon/lat: `(cos φ cos λ, cos φ sin λ, sin φ)`.
- `ê(t)` from the sub-Earth point the same way; `E(t) = delta(t) · ê(t)` (Earth's center, meters).
- `r(t)` = Sun–Moon distance → `TSI(t) = L☉ / (4π r²)`, with `L☉ = 3.828×10²⁶ W` (SOL-1). Sanity: 1320–1412 W/m².

Store as `float32` arrays: `sun_xyz[8784,3]`, `earth_xyz[8784,3]` (unit, plus `earth_dist_m[8784]`), `tsi[8784]`.

### 3.3 Local geometry (EPH-2)

For a site at latitude φ, east longitude λ, height h:

```
u = ( cosφ cosλ,  cosφ sinλ,  sinφ )     # local up
e = ( −sinλ,       cosλ,       0    )     # east
n = ( −sinφ cosλ, −sinφ sinλ,  cosφ )     # north
r_site = (R + h) · u

Sun:   d = ŝ(t)                                   (parallax ≈ 0.00006°, ignored)
Earth: d = normalize( E(t) − r_site )            (parallax ≤ ~0.26°, included)

elevation = asin( d·u )
azimuth   = atan2( d·e , d·n )   mod 2π          (0 = north, 90° = east)
```

At the pole itself `n` is undefined. Use the grid-north convention of the polar stereographic map (azimuth measured from the map's +y axis), and document it in `geometry.py`. Horizons validation compares elevations only at the pole (azimuth conventions differ there).

### 3.4 Grids and terrain (GRID, SAFE)

**Moon-wide tier**
- Plots: 1° × 1° in lat/lon (`G-<latIdx:03d>-<lonIdx:03d>`, 180 × 360 = 64,800 plots). Plot area = `R²·Δλ·(sin φ₂ − sin φ₁)`, in km² for the facts line.
- Terrain: resample the global DEM to **1/32° (~950 m at the equator)**. Each plot covers 32 × 32 cells.
- Slope: from central differences, with east-west spacing `R·cosφ·Δλ` (shrinks with latitude). Clamp near the poles; poleward of 80°S the polar tier overrides.

**South Pole District tier**
- Projection: south polar stereographic (from the GeoTIFF CRS). Core area `[TBD, default 85–90°S]` → a square of about ±151 km.
- **Analysis cells: 240 m** (config `polar.cell_m`); **plots: 1 km** (config `polar.plot_m`; must be a multiple of `cell_m`… use 960 m → 4 × 4 cells; displayed as "≈1.0 km²").
- Plot IDs: `SP-<row:04d>-<col:04d>` (row 0 at +y).
- Slopes: aggregate the **20 m slope product** into each 240 m cell as `safe_frac_cell` = share of 20 m pixels with slope < `safety.max_slope_deg` (8°). Also keep the cell's mean and P90 slope.

**Per plot (both tiers)**

| Output | Definition |
|---|---|
| `slope_mean_deg` | Mean slope over the plot |
| `slope_p90_deg` | 90th-percentile slope over the plot |
| `safe_area_frac` | Share of the plot below the slope limit |
| `roughness_m` | Standard deviation of detrended elevation in the plot |
| `relief_m` | Max − min elevation in the plot |
| `landing_safe` | `safe_area_frac ≥ safety.min_safe_frac` (0.25) |
| `hazard_score` | Mean of `norm(slope_p90)`, `norm(roughness)` and `norm(relief)`, using fixed ranges from config |

### 3.5 Terrain horizons (HOR-1)

**What:** for every polar analysis cell, the terrain horizon elevation `m(α)` at azimuths α = 0°, 2°, …, 358° (180 values), including lunar curvature.

**Algorithm** (Numba, parallel over cells):

```
for each cell c (center x0,y0; height h0 = DEM(c) + observer_mast_m [default 2 m]):
  for each azimuth α:
    best = −∞
    d = d_min (= cell_m/2)
    while d ≤ d_max (config, default 150 km):
       x, y = (x0, y0) + d · (sin α, cos α)        # straight ray in map plane (error < 0.1° within 150 km)
       h = sample(DEM pyramid by distance, x, y)   # 20 m DEM within 5 km, 80 m beyond
       drop = d² / (2R)                             # curvature
       best = max(best, atan2(h − drop − h0, d))
       d *= (1 + step_growth)                       # geometric steps, default 0.01 → ~600 samples to 150 km
    m[c, α] = best
```

**Notes and budget**
- ~1.58 M cells × 180 azimuths × ~600 samples ≈ 1.7×10¹¹ samples. That's too slow, so use a **two-level scheme**:
  1. compute at **plot resolution (960 m)** first: 91k plots, ≈ 10¹⁰ samples, about a minute on 8 cores;
  2. refine at 240 m only inside plots whose best-cell choice matters (config `polar.refine: true`), or for the whole core area if time allows.
- **Quantize for export:** `uint8 = round((m_deg + 3) / 0.16)`, which covers −3°…+37.8° (clamp). 180 bytes per plot.
- **Fallback (SOL-4):** if horizons aren't ready, use `m(α) = 0` and label the plots "simplified lighting".
- **Cross-check (HOR-2):** compare one site's horizon against a profile from Moon Trek or Quickmap, and with a synthetic test: a cone of known slope must give the analytic horizon.

### 3.6 Visibility and statistics (SOL, COMM, TEMP)

For each analysis cell (polar) or plot center (Moon-wide) and each hour `t`:

```
e_s, a_s = sun el/az;  e_e, a_e = earth el/az           (§3.3)
m_s = interp_circular(m, a_s);  m_e = interp_circular(m, a_e)   (Moon-wide: m ≡ 0)

# visible fraction of the solar disk (circular-segment area); ρ = apparent solar radius ≈ 0.2666° · (1 AU / r)
x = clamp((e_s − m_s) / ρ, −1, 1)
f_sun = (acos(−x) + x·sqrt(1 − x²)) / π                 # 0 = fully hidden, 1 = fully visible
sunlit = f_sun > 0.5

earth_ok = (e_e ≥ cutoff) and (e_e ≥ m_e)               # COMM-1, terrain-aware at the pole
```

**[DECIDE] cutoff meaning.** The requirements say "cutoff 5°" (COMM-1). Near the pole, Earth sits only a few degrees above the horizon, so an *absolute* 5° cutoff makes polar Earth contact rare. Config `comms.mode`:
- `absolute`: `e_e ≥ cutoff_deg`;
- `terrain_margin`: `e_e ≥ m_e + margin_deg` (margin default 1°).

**Decided:** `terrain_margin` with a 1° margin (team decision, 14 Nov). The absolute mode stays in config for comparison. Calibrate the margin in M2 against the sanity checks.

**Accumulated per cell over the window** (whole year for Buy; stay window for Rent):

| Statistic | Definition |
|---|---|
| `sunlit_frac` | Mean of `sunlit` |
| `longest_dark_hours` | Longest run of `not sunlit`; `longest_light_hours` likewise |
| `energy_wh_m2_per_day` | `Σ TSI · f_sun · panel_factor · 1 h / days` |
| `earth_visible_frac`, `longest_blackout_hours` | Same idea, using `earth_ok` |
| `mean_earth_elevation_deg` | Mean Earth elevation |
| `monthly` | 12 values each of sunlit % and Earth % (requirements §10) |

`panel_factor` is `cos e_s` for the vertical Sun-tracking panel (polar default) and `max(0, sin e_s)` for a horizontal panel (config `power.panel`).

**Runs and windows.** Store per cell the list of dark runs and blackout runs: (start, length), a few dozen per year. These give `best_window` (§3.9) cheaply and are the reference for the TypeScript parity tests.

### 3.7 Temperature, T1 (TEMP-1/2)

```
F_h = TSI · f_sun · max(0, sin e_s)                     # flux on the horizontal surface
T_eq = ((1 − A) · F_h / (ε σ))^(1/4)                    # A = 0.12, ε = 0.95, σ = 5.670e−8
T(t) = max(T_eq, T_floor)                                # T_floor = 95 K, or 40 K if the cell is a PSR (sunlit_frac == 0)
```

Outputs `temp_min_k`, `temp_mean_k`, `temp_max_k` and `thermal_hazard_score = mean(norm_cold(temp_min), norm_swing(temp_max − temp_min))`, using config ranges.

**Cross-check (TEMP-4):** sample LRO Diviner polar maps at a few plots and record the differences in `docs/validation.md`.

### 3.8 Plots, land, landmarks, ice

- **Best cell** (polar): the cell with the highest viability (§3.9) among the plot's cells that pass the safety gate. Light, comms and temperature facts come from the best cell; area facts (buildable %, slopes, relief) from the whole plot (GRID-5).
- **Land type** (LAND-1), rules in priority order:
  1. `sunlit_frac < 0.01` → **PSR**;
  2. polar and `sunlit_frac ≥ config.land.peak_light_frac` (0.7) → **Peak of light**;
  3. `|lon| > 90°` → **Far side**;
  4. local relief or position: crater rim / crater floor, using a topographic position index of elevation vs. the 5 km neighborhood mean;
  5. otherwise **Mare** if the elevation is below the global median − 1 km, else **Highlands**.
- **Landmarks** (LAND-2/3): great-circle distance from each plot center to each landmark (vectorized). `nearby` = up to 5 within `config.landmarks.radius_km`. `landmark_score = max over landmarks of fame_weight · exp(−d / d0)`, where fame weights are 1.0 for Apollo/Artemis, 0.6 for named major craters and 0.3 for others.
- **Ice** (ICE-1): PSR mask at cell level → `scipy.ndimage.distance_transform_edt` in map meters → `ice_km` per plot (best cell). Moon-wide plots: `null`.

### 3.9 Scoring (VS)

**Normalization** uses fixed ranges from config (VS-2): `norm(x; lo, hi) = clamp((x − lo)/(hi − lo), 0, 1)`.

**Penalty:** `penalty(h; h50, k) = 1 / (1 + (h/h50)^k)`, a smooth logistic in hours (config per metric; e.g. dark `h50 = 120 h, k = 2`).

```
s_safety   = 1 − hazard_score
s_power    = norm(energy) · penalty(longest_dark_hours)
s_comms    = earth_visible_frac · penalty(longest_blackout_hours)
s_thermal  = 1 − thermal_hazard_score
s_landmark = landmark_score
s_ice      = 1 − norm(ice_km; 0, ice_max_km)            (polar; 0 elsewhere)

viability = 100 · Σ wᵢ sᵢ / Σ wᵢ          if landing_safe else min(cap, …)   (cap = 10, Off market)
named scores = round(100 · sᵢ)            → Landing, Sun, Signal, Comfort, Views, Ice
```

**Home types (FIL-4, VS-7)**
- **Match %:** `match = 100 · Σ w_type,i sᵢ / Σ w_type,i`, computed client-side from the shipped sub-scores.
- **Gates over reference stays (v2.2 F1):** for each plot and type with a reference stay `L` (Lander pad 14 d, Habitat 90 d), compute `best_window`. Over daily start dates `s` in the year, find the start that minimizes the gated metric (longest night or longest blackout) within `[s, s+L]`, using the run lists (§3.6): clip each run to the window and take the max. Cost: ~366 starts × ~30 runs per plot, so seconds in Numba.
- Export the minimum and its start date per type.
- **Calibration (M3):** a script prints, per type and gate value, how many plots pass. The team picks values that give ≥ 50 polar results, then writes them into config.

### 3.10 Pricing, rent, badges, blurbs (PRICE, RENT, DET-11, DET-6)

```
price = BASE · exp(k · viability/100) · (1 + landmark_premium) · scarcity
        BASE = 5,000;  k = 6.9  → viability 0 ≈ $5K, 50 ≈ $160K, 100 ≈ $5M (≈ $10M with premiums)  (config)
        scarcity = config.price.scarcity_mult if viability ≥ config.price.scarcity_viability_cutoff else 1
        (the pipeline writes the cutoff = the viability at the top-N% quantile into config.json — v2.2 F4)
range = price · (1 ∓ u_tier),   u_tier = 0.25 (Moon-wide) / 0.10 (polar)
rent_avg_usd_month = RENT_RATIO · price                    # = the 1-year-stay rent (v2.2 F3)
display rounding: 3 significant figures → "$4.2M", "$340K"
```

**Rent for a stay** (RENT-2, client-side; Python reference in `pricing.py`): recompute SOL, COMM and TEMP statistics over `[move_in, move_in + stay]` for the plot's best cell (§3.6 formulas), then `viability_stay`, then `rent_per_month = RENT_RATIO · price(viability_stay)`. Safety and landmark terms stay as they are.

**Badges**

| Badge | Rule |
|---|---|
| Hot property | Viability ≥ the 95th percentile (all plots) |
| Earth view | (Polar, or limb with `80° ≤ |lon| ≤ 100°`) and `earth_visible_frac ≥ 0.95` |
| Peak of light | Land type is Peak of light |
| Price cut | Rent only: stay rent ≤ 0.9 · `rent_avg_usd_month` |
| Off market | `not landing_safe` |

At most 2 badges per card, in priority order: Off market > Hot property > Peak of light > Earth view > Price cut.

**Blurbs** (DET-6): 20–30 templates keyed on thresholds (e.g. `sunlit ≥ 0.8` → "near-constant sun"; `ice_km ≤ 5` → "cozy −230 °C basement next door"). The template choice is a deterministic hash of the plot ID, so blurbs are stable across runs. Templates live in `config/blurbs.yaml`.

### 3.11 Export (§5 formats)

The pipeline writes `app/public/data/` (or `data/out/` and copies it), plus `manifest.json` containing:
- the pipeline git SHA, config hash and analysis year;
- a file list with byte sizes and SHA-256;
- the counts per tier.

### 3.12 Validation and sanity tests

- **EPH-3:** `python -m lunar_listings validate` queries Horizons at 3+ sites × 3+ dates. It writes `docs/validation.md` (table plus the plot `docs/img/validation.png` for slide 6) and **fails CI** if the polar elevation error is > 0.1° or the Moon-wide error is > 1°.
- **Sanity suite** (pytest, on the real outputs): every requirements §9 check, with tolerances. For example:
  - near-side `earth_visible_frac` ≥ 0.99;
  - far-side center ≤ 0.01;
  - equator `sunlit_frac` 0.5 ± 0.02;
  - equator longest dark 350 ± 10 h;
  - TSI in [1315, 1415];
  - a Shackleton floor cell `sunlit_frac` < 0.01;
  - each Home type returns ≥ the minimum results.

---

## 4. Configuration (`config/lunar-listings.yaml`)

Abridged; all values are defaults to tune in M0/M3.

```yaml
analysis: { year: 2028, step_hours: 1 }
moon: { radius_m: 1737400 }
grid:
  global: { plot_deg: 1.0, terrain_res_deg: 0.03125 }
  polar:  { lat_min: -85.0, cell_m: 240, plot_m: 960, refine: false }
horizon: { az_step_deg: 2, d_max_m: 150000, step_growth: 0.01, mast_m: 2.0, near_dem_radius_m: 5000 }
power:  { panel: vertical_tracking, area_m2: 10, efficiency: 0.30, sunlit_threshold: 0.5 }
comms:  { mode: terrain_margin, cutoff_deg: 5.0, margin_deg: 1.0 }
thermal: { albedo: 0.12, emissivity: 0.95, floor_k: 95, psr_floor_k: 40, cold_range_k: [40, 120], swing_range_k: [100, 300] }
safety: { max_slope_deg: 8.0, min_safe_frac: 0.25, slope_p90_range: [0, 30], roughness_range_m: [0, 50], relief_range_m: [0, 2000] }
norm:   { energy_wh_m2_day: [0, 30000] }
penalty: { dark: { h50: 120, k: 2 }, blackout: { h50: 120, k: 2 } }
weights: { safety: 0.30, power: 0.25, comms: 0.20, thermal: 0.15, landmark: 0.10, ice: 0.0 }
home_types:
  lander_pad: { weights: { safety: 0.4, power: 0.35 }, ref_stay_days: 14, gates: { longest_night_h: 48 } }
  habitat:    { weights: { comms: 0.35, thermal: 0.25 }, ref_stay_days: 90, gates: { longest_blackout_h: 72 } }
  solar_farm: { weights: { power: 0.6 }, ref_stay_days: 366, gates: { safe_area_frac: 0.4, sunlit_frac: 0.6 } }
  ice_depot:  { weights: { ice: 0.45, power: 0.25 }, ref_stay_days: 366, gates: { ice_km: 10 }, polar_only: true }
  min_results: 50
price: { base_usd: 5000, k: 6.9, scarcity_top_pct: 2, scarcity_mult: 1.3, apollo_premium: 0.25, apollo_radius_km: 50, peak_light_premium: 0.5,
         range: { global: 0.25, polar: 0.10 }, rent_ratio: 0.006 }
badges: { hot_property_pct: 95, earth_view_frac: 0.95, price_cut_frac: 0.10, max_per_card: 2 }
results: { max_cards: 200 }
stays: [14, 30, 90, 366]
```

`config.py` validates types and ranges and writes `config.json` (plus the computed `scarcity_viability_cutoff`) for the app.

---

## 5. Data formats (pipeline → app)

All under `app/public/data/`. Little-endian. Gzip/brotli are left to the host.

| File | Format | Contents | Size (est.) |
|---|---|---|---|
| `manifest.json` | JSON | Versions, hashes, counts, file list | < 10 KB |
| `config.json` | JSON | Exported config + computed cutoffs | < 10 KB |
| `ephemeris.bin` | float32 | `sun_xyz[8784×3]`, `earth_xyz[8784×3]`, `earth_dist_m[8784]`, `tsi[8784]` | ~280 KB |
| `global/cols.bin` + `global/cols.json` | columnar | One typed array per attribute (schema below), 64,800 rows | ~2 MB |
| `polar/cols.bin` + `polar/cols.json` | columnar | Same, ~91k rows | ~3 MB |
| `polar/horizon/<tx>_<ty>.bin` | uint8 | 180 bytes per plot, rows ordered by plot index within the tile (16 × 16 tiles) | ~16 MB total, lazy |
| `<tier>/detail/<tx>_<ty>.json` | JSON | Per-plot detail records (requirements §10 record minus the columns already shipped) | ~30–50 MB total, lazy |
| `<tier>/overlay/<name>.png` + `.json` | PNG + legend | One raster per overlay in the tier's map projection, plus the color ramp/legend | ~1–3 MB each |
| `<tier>/basemap.jpg` | JPEG | Hillshade or imagery in map projection (global 8192×4096; polar 4096×4096) | ~3–6 MB each |
| `landmarks.json` | JSON | Names, types, coordinates, fame | < 200 KB |

**Columnar schema** (`cols.json` lists name, dtype, offset, scale):

| Column | Type | Notes |
|---|---|---|
| `x`, `y` | float32 | Map coordinates of the plot center (projected meters for polar; degrees for global) |
| `lat`, `lon` | float32 | — |
| `area_km2` | float32 | — |
| `price` | float32 | USD |
| `rent_avg` | float32 | USD/month |
| `viability` | uint8 | — |
| `s_safety … s_ice` | uint8 | 6 columns, 0–100 |
| `sunlit_pct`, `earth_pct` | uint8 | — |
| `slope_mean_ddeg` | uint16 | 0.1° units |
| `longest_dark_h`, `longest_blackout_h` | uint16 | — |
| `temp_min_k`, `temp_max_k` | uint16 | — |
| `ice_km10` | uint16 | 0.1 km units; 65535 = n/a |
| `land_type` | uint8 | Enum |
| `flags` | uint16 | Bitmask: off_market, badges, tier |
| `bw_lander_h`, `bw_habitat_h` | uint16 | `best_window` metric values |
| `bw_lander_start`, `bw_habitat_start` | uint16 | Day of year |
| `tile` | uint16 | Detail and horizon tile index |
| `row_in_tile` | uint16 | — |

The **stub generator** (`pipeline/lunar_listings/stub.py`, M0) writes every file above with plausible fake values, so the frontend builds against the real formats from hour one.

---

## 6. Frontend

### 6.1 Stack

| Purpose | Choice |
|---|---|
| Build, UI, language | Vite, React 18, TypeScript (strict) |
| Map | deck.gl (`OrthographicView`; `BitmapLayer`, `ScatterplotLayer`, `TextLayer`, `PolygonLayer`) |
| State | Zustand |
| Results list | react-window (virtualized) |
| Charts | Recharts (rent history) |
| 3D Tour | Canvas 2D |
| Tests | Vitest, Playwright |

No server.

### 6.2 Modules

```
src/
  data/       loader.ts (manifest, cols.bin → typed arrays, lazy tiles, cache), types.ts
  geo/        projections.ts (polar stereographic ⇄ lat/lon; equirect), geometry.ts (ENU, az/el — mirrors §3.3)
  science/    visibility.ts, stats.ts, rent.ts, scoring.ts   (mirror Python; golden-vector tested)
  worker/     compute.worker.ts  (filters/sort over typed arrays; rent; live visibility; tour paths)
  state/      store.ts (tab Buy/Rent, tier, filters, homeType, sort, overlay, time, selection, moveIn, stay)
  map/        MapView.tsx (layers below), markers.ts (dot↔pill by zoom, MAP-2), selection.ts
  results/    ResultsList.tsx, ListingCard.tsx (virtualized, capped 200, RES-1..4)
  listing/    Listing.tsx, Gallery.tsx (Photos | 3D Tour), FactsLine.tsx, Scores.tsx, Facts.tsx,
              RentHistory.tsx, Nearby.tsx, FinePrint.tsx, Badges.tsx
  tour/       TourCanvas.tsx (panorama renderer)
  header/     Header.tsx (logo, Buy|Rent, search), Filters.tsx (Price, Home type, Land type, More, Overlays), RentControls.tsx
  modes/      demo.ts (?demo=1 presets), present.css (?present=1)
  ui/         tooltips (D-1 text from config/glossary.json), fine print, theme tokens
```

### 6.3 Map layers (bottom → top)

1. `BitmapLayer` basemap, in tier coordinates.
2. `BitmapLayer` overlay (selected OV-*), with an opacity slider (OV-10).
3. Comm-window overlay (OV-7): computed live in the worker for visible plots at slider time, drawn as a `ScatterplotLayer` mask.
4. Markers:
   - zoomed out: `ScatterplotLayer` dots colored by price band;
   - zoomed in: `TextLayer` + background price pills;
   - Off market: grey dots with a distinct outline shape (MAP-5).
5. `PolygonLayer` hover and selection outline.

Picking uses deck.gl's GPU picking. Hovering a marker highlights its card (MAP-3).

### 6.4 Interaction and data flow

- **Startup:** fetch manifest → config → both tiers' `cols.bin` (~5 MB) → basemaps. Interactive in < 3 s (NFR-1); overlays load on demand.
- **Filter, sort, Home type:** the worker scans typed arrays (~155k rows, < 20 ms), applies gates (Home type `bw_*` and static facts), computes match %, sorts, and returns the top 200 indices plus the count (RES-1, NFR-2).
- **Select a plot:** lazy-load its detail tile (and horizon tile for polar), then render the listing. The facts line comes from the columns, so it's instant.
- **Time slider:** sets `t`; the worker recomputes instantaneous Earth visibility for visible plots (OV-7) and Sun/Earth positions for the 3D Tour (TIME-2). The Buy price never changes (D-6), and an e2e test asserts it.
- **Rent:** on move-in or stay change, the worker runs `rent.ts` for the selected plot. That's 8,784 hours × a few operations, < 5 ms (NFR-10). It returns `/mo`, the total, the change vs. `rent_avg` with its reason (which metric changed most) and the Price cut badge (RENT-1..3).
- **Rent history (DET-7):** 12 stays of one month each, computed in the worker on selection.

### 6.5 3D Tour renderer (DET-5)

- **Canvas panorama:** x = azimuth 0–360° (N at center, configurable); y = elevation −3°…+15° with **vertical exaggeration** (labeled "vertical scale ×N") so the skyline reads.
- **Drawn elements:**
  - the terrain silhouette `m(α)` from the horizon tile;
  - the Sun path over the selected window, as dots colored visible / behind terrain;
  - the Earth path the same way;
  - current Sun and Earth markers at slider `t`;
  - countdown text, from scanning forward from `t` to the next change of `sunlit` / `earth_ok`.
- Moon-wide plots have no tour tab (no horizon data). Fallback lighting shows a flat line plus the label (SOL-4).

### 6.6 Modes

- `?demo=1`: forces local data and preloaded scenarios (far-side bargain, Shackleton rim, rent shift) with one-click buttons (PRS-2).
- `?present=1`: 1920×1080 layout, enlarged type and markers, dev controls hidden (PRS-3).
- URL state for filters/sort/selection is P2 (FIL-6).

### 6.7 Accessibility and copy

- Keyboard-focusable cards and markers (via list focus).
- Badges and verdicts always carry text.
- Colorblind-safe ramps (viridis/cividis; diverging for temperature).
- All tooltip text in `config/glossary.json` (D-1), with the formula and source for students (DET-8).

---

## 7. Testing

| Layer | Tool | What |
|---|---|---|
| Geometry | pytest | ENU orthonormality; az/el for known vectors; pole convention; Earth parallax magnitude |
| Horizons | pytest | Synthetic cone/plane DEM → analytic horizon within 0.05°; curvature-only case; quantization round-trip |
| Visibility/stats | pytest | Disk-fraction formula at ±ρ; run-length on crafted sequences; equator smooth-Moon ≈ 50% / 355 h |
| Scoring/pricing | pytest | Monotonicity (higher viability → higher price); determinism; RENT-5 (1-yr rent = ratio × price); badge rules |
| **Parity** | pytest + vitest | `tests/golden/*.json`: inputs + expected outputs for geometry, visibility, stats, rent, scoring. Python writes them, TypeScript must match (tolerance 1e-4 or 1 unit) |
| Real-data sanity | pytest | Requirements §9 list (§3.12) |
| Validation | script | EPH-3 report + plot |
| Frontend unit | vitest | Loader decoding, projections, store logic, marker switch |
| E2E | Playwright | Load offline; click card → listing; switch tier; 3D Tour renders; Rent shift changes rent **and not** Buy price; filters/sort; ≤ 3 s load on CI runner (smoke) |
| Performance | Playwright trace | Filter/sort < 200 ms; slider ≥ 15 fps |

---

## 8. Build, run, deploy

| Command | Does |
|---|---|
| `make setup` | `uv venv && uv pip install -e pipeline[dev]`; `cd app && npm ci` |
| `make stub` | Write stub data to `app/public/data/` (M0/M1 frontend work) |
| `make fetch` | Download and verify DEMs + gazetteer; Horizons query (or use the committed CSV) |
| `make data` | All pipeline stages → `app/public/data/` |
| `make validate` | EPH-3 + sanity suite → `docs/validation.md` |
| `make test` | pytest + vitest |
| `make app` | `npm run build` → `app/dist/` |
| `make demo` | Serve `app/dist` locally, offline, `?demo=1` |

- **CI** (GitHub Actions): lint (ruff, eslint), pytest (unit + golden; real-data sanity only if data is present), vitest, build, and Playwright smoke against the stub data.
- **Deploy:** GitHub Pages from `app/dist` (with base path) on push to `main`.
- **Data in git:** commit `app/public/data/` only if under ~50 MB. Otherwise publish it as a GitHub Release asset that `make data-download` fetches. Raw DEMs are never committed (DAT-3).

---

## 9. Work breakdown by milestone and track

| Milestone | Data A (geometry) | Data B (terrain/scoring) | Frontend | Presentation |
|---|---|---|---|---|
| **M0** | Verify Horizons queries by hand | Config skeleton; `stub.py` with final formats (§5) | Vite/React/deck.gl skeleton; loader | Story, asset folder |
| **M1** | Fetch + parse ephemeris; `geometry.py` | DEM fetch/resample; slope/roughness/relief | Basemaps; dots/pills; results list; listing on stub | Skeleton screenshot |
| **M2** | Visibility + stats (smooth Moon); EPH-3 validation | Systems A, C; sanity suite | Overlays plumbing; worker scaffold | Validation plot |
| **M3** | Golden vectors v1 | Scoring, pricing, badges, `best_window`; gate calibration; export | Real data; facts line; Off market; filters; sort | Near/far side captures |
| **M4** | Horizons (Numba); terrain-aware stats | Polar grid; PSR/ice; polar export | South Pole view; 3D Tour; horizon tiles | 3D Tour hero clip |
| **M5** | — | Land types; landmarks; blurbs | Home type, scores, badges, range, "Plots for you" | Home-type captures |
| **M6** | `rent.ts` parity | Monthly arrays | Rent tab; rent history; time slider; OV-7 | Before/after number |
| **M7** | — | Diviner cross-check doc | Demo/presentation modes; accessibility; perf | Novice test |
| **M8** | Freeze | Freeze | Freeze, deploy | Video, deck, project page |

**Task-level breakdown with hours, owners and "done when" checks: `docs/build-plan.md`.**

**Interface freezes:** data formats (§5) and `config.json` keys at **M0**; golden-vector schema at **M3**. Any change after a freeze needs a note in `docs/progress.md`, plus a stub/golden update in the same commit.

---

## 10. Technical risks and open items

| # | Item | Plan |
|---|---|---|
| T1 | **Frame consistency:** Horizons sub-points use its Moon rotation model, LOLA uses MOON_ME (DE421). Differences are small (sub-km), so angular errors are far below 0.1°. | Document in DAT-2; EPH-3 validation would catch a sign or convention error. |
| T2 | **Horizons longitude sign convention:** stated at the end of each output. | Parser reads it and asserts it; validation catches a mistake. |
| T3 | **Comms cutoff semantics** (§3.6). | **Decided:** `terrain_margin` (1°). Calibrate in M2. |
| T4 | **Horizon compute budget.** | Plot-resolution first, refine optional; Numba parallel; precompute once and cache. |
| T5 | **Pole azimuth convention.** | Grid-north on the polar map; validate elevations only at the pole. |
| T6 | **Python/TypeScript drift** (D4/D5). | Golden vectors in CI. |
| T7 | **Payload size.** | Columnar + lazy tiles; measure at M3/M4 against NFR-4; drop refine or shrink the core area if needed. |
| T8 | **Basemap rendering for the global tier near the poles** (equirectangular distortion). | The polar tier takes over poleward of the core area; the global tier is the "hook" view. |
| T9 | **Push from automation is blocked in this environment.** | Team members push from their own machines. |
| T10 | **Price scale:** with v2.1's BASE = $50,000 the cheapest possible plot would be $50K, contradicting "worst in the low thousands". | Fixed in requirements v2.2 (F9): BASE = $5,000, k = 6.9. |

---

## Appendix A: Formula summary

| Quantity | Formula |
|---|---|
| TSI | `L☉ / (4π r²)` |
| Elevation / azimuth | `asin(d·u)`, `atan2(d·e, d·n)` |
| Earth direction | `normalize(delta·ê − (R+h)u)` |
| Solar-disk fraction | `(acos(−x) + x√(1−x²))/π`, with `x = clamp((e−m)/ρ, −1, 1)` |
| Curvature drop | `d²/(2R)` |
| T1 | `((1−A)F_h/(εσ))^¼`, floored |
| Penalty | `1/(1+(h/h50)^k)` |
| Viability | `100 Σwᵢsᵢ/Σwᵢ` (gated) |
| Price | `BASE·e^{k·v/100}·(1+premium)·scarcity` |
| Rent | `RENT_RATIO·price(v_stay)` |

## Appendix B: References

- Requirements v2.2: `docs/requirements.md` · Milestones: `docs/milestones.md` · Presentation: `docs/presentation.md`
- JPL Horizons manual (observer quantities 14, 15, 19, 20; site coordinates): https://ssd.jpl.nasa.gov/horizons/manual.html · API: https://ssd.jpl.nasa.gov/api.html
- PGDA LOLA south-pole products: https://pgda.gsfc.nasa.gov/products/90
- USGS LOLA global DEM: https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif
- deck.gl `OrthographicView`: https://deck.gl/docs/api-reference/core/orthographic-view
