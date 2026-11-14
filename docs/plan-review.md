# Lunar Landing Site Navigator — Plan Review & Refined Requirements

*NASA Space Apps Challenge 2026 · Team planning doc · Reviewed against the official challenge brief and Resources tab*

## TL;DR

Our plan is ambitious and covers more than the brief asks for (terrain safety, temperature, a viability score). But it is **missing the brief's centerpiece**, a view of the Sun and Earth relative to the *local horizon* with time-to-sunset and time-to-Earthset. Its **data pipeline also can't produce what the rest of the plan needs**:

- The Horizons queries ignore terrain.
- They only cover one point.
- The global DEM we picked is distorted at the poles.

The fix is a precomputed **horizon-mask** pipeline that feeds every other system.

**Top 5 changes**

1. Add a **site sky view**: a polar plot of the terrain horizon with the Sun and Earth tracks, plus sunset and Earthset countdowns and a timeline strip.
2. Replace the per-site Horizons calls with **one ephemeris query** (sub-solar and sub-Earth points), then compute azimuth and elevation ourselves for any site.
3. Switch to the **NASA PGDA south-polar stereographic LOLA DEMs**, and compute **terrain horizon masks** offline.
4. Define the **viability score** explicitly: hard constraints mark a site red, and a weighted soft score ranks the rest.
5. Add **curated sites, side-by-side comparison, and a "what if we slip?" date sweep**. All three are named in the brief.

---

## 1. What the brief asks for that the plan doesn't cover yet

The brief is built around one deliverable: **visualize the Sun's and Earth's positions relative to the horizon** at a chosen site and date, to assess power and direct-to-Earth comms. It also suggests showing **time remaining before sunset or Earthset**.

### 1.1 Site sky view (new; highest priority)

- **Polar plot.** Show the terrain horizon around the site, with the Sun's and Earth's paths over the mission. Where a path dips behind terrain, that's a blackout.
- **Countdowns.** "Sun sets in X h" and "Earth sets in Y h", measured from any point on the timeline.
- **Timeline strip.** Two bars across the mission duration: sunlit / dark and comms / no comms.

### 1.2 Other brief items to add

- **Curated site list plus custom coordinates.** For the south pole, use NASA's nine Artemis III candidate regions:
  - Peak near Cabeus B
  - Haworth
  - Malapert Massif
  - Mons Mouton Plateau
  - Mons Mouton
  - Nobile Rim 1
  - Nobile Rim 2
  - de Gerlache Rim 2
  - Slater Plain
- **Side-by-side comparison** of 2–4 sites.
- **"What if we slip?" date exploration.** This is a main theme of the brief. Build a heatmap with candidate landing dates across, sites down, and viability score as the color. It answers "launch slipped 3 weeks, where do we go now?"
- **Explainer mode for educators and the public.** For example, show why moving a few km turns 80% sunlight into 20%.

---

## 2. Data pipeline corrections

### 2.1 Horizons vector query: wrong tool

- The plan describes it as "distances between the geocenter and the earth". It actually returns the **geocenter → target** vector, where the target is the Sun (`10`) or the Moon (`301`).
- A distance alone can't give elevation angles at a lunar site.
- **Action:** drop it, or keep it only for the Sun–Moon distance used in the 1/r² solar flux.

### 2.2 Horizons observer query: one point, no terrain

`coord@301` with `SITE_COORD='0,-89.9,0'` gives Earth's elevation measured from a **smooth sphere** at a single point. This has three problems:

- A crater-floor site and a ridge site get identical answers. The brief explicitly warns that with no atmosphere, **local terrain sets the horizon**.
- It needs one API call per site per time range, which won't scale to map overlays.
- **The 1-day step is far too coarse.** The Sun circles the full horizon about once every 29.5 days (roughly 12° of azimuth per day). Use **1 h** steps.

### 2.3 Recommended approach: one query, then local math

1. Run **one Horizons OBSERVER query**:
   - target `301`, center `500@399`
   - `QUANTITIES='14,15,20'` (sub-observer point, sub-solar point, range)
   - `STEP_SIZE='1h'`, covering 2026–2030

   This gives the **sub-Earth and sub-solar points on the Moon** every hour. Save it as a static file.
2. Turn those into Sun and Earth direction vectors in the Moon-fixed frame. For any site, rotate them into local East-North-Up → azimuth and elevation.
   - Include **Earth parallax** (≈0.26°, because the site is offset from the Moon's center).
   - Sun parallax is negligible.
3. **Validate** against direct `coord@301` queries at 2–3 sites. This doubles as a "we used a NASA source correctly" point for judges.

### 2.4 DEM: switch from the global 118 m TIFF

The global equirectangular product is heavily distorted near the poles and large. Use the **NASA GSFC Planetary Geodesy Data Archive (PGDA)** south-polar stereographic LOLA products instead. They are cloud-optimized GeoTIFFs in meters and include:

| Product | Use |
|---|---|
| `LDEM_80S_20MPP_ADJ.TIF` (~2.6 GB) | Near-field height |
| `LDEM_80S_80MPP_ADJ.TIF` (much smaller) | Far-field height for horizon masks |
| `LDSM_*` | Ready-made slope maps (degrees) |
| `LDEM_*_ERR`, `LDSM_*_ERR` | Height and slope uncertainty → confidence display |
| `LDRM_80S_*_ROUGH_*` | Multi-baseline roughness |
| 5 m/px mosaic, 87–90°S | Zoom-in detail for finalist sites |

---

## 3. New core system: horizon masks

Every other system depends on this, so it should be in the plan explicitly.

- **Definition.** For each grid cell, compute the terrain horizon elevation at each azimuth by marching outward and keeping the maximum of `atan((h − h0 − d²/2R) / d)`. The `d²/2R` term is lunar curvature (R = 1737.4 km).
- **Search distance.** Look out **tens of km**, because distant massifs matter at the pole. Use the 80 m DEM for the far field and the 20 m DEM nearby.
- **Visibility tests.**
  - Sun: `sun_el > mask(sun_az)`. Better: compute the **fraction of the solar disk** above the mask, because the disk is ~0.53° wide and at the pole the Sun skims the horizon.
  - Earth: `earth_el > mask(earth_az) + antenna_margin`.
- **Size budget.** A 240 m grid over 88–90°S is ~250k cells. At 180 azimuths stored as uint8, that's ~45 MB. Compute it **offline** in Python (numpy or numba) and ship it as a static asset.
- **Mast height.** Make solar-array and antenna height an input; it's just a raised `h0`. NASA's LOLA work found that at 5 m above the surface, DEM uncertainty has much less effect on illumination.

---

## 4. Spec tightening per system

### 4.1 Physical landing site safety

Turn "slant / space / chasms, mountains, cliffs" into measurable criteria:

| Criterion | Definition | Default |
|---|---|---|
| Slope | PGDA slope map, per cell | ≤ 10° (user-adjustable) |
| Space | Landing ellipse radius input; site passes if ≥ N% of cells inside pass the slope test | 100 m radius, N = 95% |
| Roughness | PGDA roughness map at a lander-scale baseline | Threshold TBD |
| Cliffs / chasms | Max slope or elevation range inside the ellipse | Flag if exceeded |

**Be honest about limits.** Boulders are below DEM resolution, and even the best LOLA maps carry ~1.5–2.5° RMS slope error. Show this as a confidence note on each site.

### 4.2 Solar power generation

- **Panel model.** At the pole the Sun stays within about ±1.5° of the horizon, so horizontal panels produce close to nothing. Default to **vertical panels that track the Sun in azimuth**.
- **Power:** `P = (1361 W/m² / r_AU²) × area × efficiency × visible_disk_fraction`
- **Metrics:**
  - % of mission time sunlit
  - total energy (Wh)
  - **longest continuous darkness**. This matters more than average sunlight because it sets battery size, so make it a **hard constraint**.

### 4.3 Moon-to-Earth communication

- **Drop "Speed".** The Earth–Moon distance is nearly constant, so data rate depends on the hardware, not the site.
- **Replace "Reliability" and "Frequency of use"** with:
  - % of time Earth is visible
  - **longest comms gap**
  - number of windows
  - time to next Earthset
- **Key insight for the explainer.** Earth sits roughly in the direction of the near side and only wobbles a few degrees with libration. So whether a site has comms depends mostly on whether terrain blocks that one direction, which is very different from sunlight.
- **Deep Space Network (stretch goal).** Minimum version: the Moon is ≥ 10° above the horizon at one or more of Goldstone, Madrid or Canberra. That is nearly always true.

### 4.4 Temperature

- **Clarify the equation note.** It defines Z as latitude, but in the heat equation Z is normally **depth**. Solving that equation is too much for a hackathon.
- **Use measured data: the LRO Diviner south-polar products** (another NASA source). They are binned at 240 m by **24 subsolar-longitude bins (diurnal) × 6 seasonal bins**, which maps directly onto our date axis.
- **Fallback for sunlit pixels:** radiative equilibrium, `T = [(1−A)·S·sin(el) / (εσ)]^¼`.
- **Label it "surface thermal environment"**, not equipment temperature.

---

## 5. Viability score: explicit definition

**Hard constraints.** A site is marked **red** if any of these is true:

- it fails the slope or landing-ellipse check
- longest darkness > the user's limit
- longest comms gap > the user's limit
- temperature goes outside the user's range (if one was set)

**Soft score (0–100).** A weighted sum of normalized metrics over the **entire mission duration**:

- sunlit %
- energy
- comms %
- comms gap length
- slope margin

Users adjust the weights with sliders. "Maximize by default" means using the default weights.

**Always show the raw metrics next to the score.** Planners won't trust a single number on its own.

---

## 6. Inputs, scope, and cleanup

- **Merge "Mission Duration" and "Mission Dates"** into a **start date plus a duration**. Having both is redundant and can contradict itself.
- **Fill in the TBD default mission profile:**

  | Parameter | Default |
  |---|---|
  | Start date | a 2027 date |
  | Duration | 10 Earth days |
  | Panels | Vertical, azimuth-tracking, 2 m mast |
  | Antenna elevation mask | 5° |
  | Max slope | 10° |
  | Landing ellipse | 100 m radius |
  | Max continuous darkness | 48 h |
  | Temperature limits | None |

- **Restrict to the south pole (80–90°S).** The brief, the data and the candidate sites are all there. Supporting the north pole doubles the preprocessing for no judging benefit.
  - Optional: add 1–2 equatorial reference sites (e.g. Apollo 11) using the smooth-sphere horizon, as an explainer contrast.
- **Overlays.**
  - Merge "Lighting characteristics" and "Solar power".
  - Rename "Communication strength" to **comms availability %**.
  - The comms window is binary at a given time (as the plan already notes), so show it in the timeline and sky view, not as a gradient.
- **Cut** "Effort to get to landing site", as the plan already flags.
- **AI integration: pick one concrete feature, and don't let it gate the demo.** Options:
  - a natural-language query, e.g. "best site with ≥ 70% sun in March 2027"
  - an auto-written explanation of why site A beats site B, generated from the computed metrics

---

## 7. Architecture for "snappy and cross-platform"

**Offline, in Python:**
1. Fetch the Horizons ephemeris once.
2. Compute horizon masks from the PGDA DEMs.
3. Export static assets: masks, slope and roughness tiles, Diviner lookups, and the hourly ephemeris table.

**Web app:**
- Given a date range, compute visibility, power, comms and scores **in the browser** in a Web Worker.
- Map: deck.gl or Leaflet with a polar projection. Optional 3D view with three.js.
- **No live API calls at runtime.** That avoids Horizons rate limits and latency, and makes it cross-platform for free.

---

## 8. Action checklist

| # | Task | Owner | Status |
|---|---|---|---|
| 1 | Horizons ephemeris fetch script (sub-solar and sub-Earth, 1 h, 2026–2030) | | ☐ |
| 2 | Site az/el math + validation against `coord@301` | | ☐ |
| 3 | Download PGDA DEMs (80 m + 20 m) and slope/roughness/error maps | | ☐ |
| 4 | Horizon-mask generator (offline) | | ☐ |
| 5 | Power, comms and darkness metrics per cell and per site | | ☐ |
| 6 | Diviner temperature lookup | | ☐ |
| 7 | Viability score + hard constraints | | ☐ |
| 8 | Map with overlays + red unusable areas | | ☐ |
| 9 | Site sky view (polar plot, countdowns, timeline) | | ☐ |
| 10 | Curated sites + side-by-side comparison | | ☐ |
| 11 | Date-slip heatmap | | ☐ |
| 12 | Explainer mode / AI feature (stretch) | | ☐ |

---

## NASA data sources used

- **JPL Horizons System**: ephemerides. https://ssd.jpl.nasa.gov/horizons/ · manual: https://ssd.jpl.nasa.gov/horizons/manual.html
- **LRO LOLA via NASA GSFC PGDA**: south-polar DEMs, slope, roughness, error maps. https://pgda.gsfc.nasa.gov/products/90 · 5 m site DEMs: https://pgda.gsfc.nasa.gov/products/78
- **LRO Diviner**: polar surface temperatures (PDS). https://www.diviner.ucla.edu/data
- **Moon Trek / Quickmap**: basemap imagery and cross-checking. https://trek.nasa.gov/moon/ · https://quickmap.lroc.asu.edu/

## References

- Challenge brief: https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/
- Barker et al. (2021), *Improved LOLA Elevation Maps for South Pole Landing Sites*, PSS 203, 105119. https://doi.org/10.1016/j.pss.2020.105119
- Mazarico et al. (2011), *Illumination conditions of the lunar polar regions using LOLA topography*, Icarus 211. https://doi.org/10.1016/j.icarus.2010.10.030
- Williams et al. (2019), *Seasonal polar temperatures on the Moon*, JGR Planets.
- NASA Artemis III candidate regions (Oct 2024): https://www.upi.com/Science_News/2024/10/28/nasa-artemis-moon-landing-regions/5971730152372/
