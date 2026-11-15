# Lunar Listings: resources used and what they mean

One place to see every dataset, service and tool in the project, what it is, and how we use it. Sources, sizes and SHA-256 checksums of the raw data are in `pipeline/data/sources.yaml`; the formulas are in `docs/technical-spec.md` §3 and the values in `config/lunar-listings.yaml`.

**Input** = the result depends on it. **Check** = used only to test our results, never to compute them.

## 1. NASA and USGS data

| Resource | Provider | Role | What it is | How we use it |
|---|---|---|---|---|
| **JPL Horizons** (`ssd.jpl.nasa.gov/api/horizons.api`) | NASA JPL | Input and check | NASA's ephemeris service: where solar-system bodies are, to high accuracy | One query for hourly Sun and Earth directions and distances as seen from the Moon, for all of 2028 (366 × 24 = 8,784 steps). Saved as `pipeline/data/ephemeris_2028.csv`, so the pipeline runs offline. Gives sunlight, Earth contact, and solar energy (the Sun's distance sets its brightness). Also queried live by `validate` to test our own geometry (worst error 0.006°). |
| **LRO LOLA global DEM**, 118 m (`Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif`) | USGS (from NASA LRO) | Input | Height of the whole Moon, measured by the Lunar Orbiter Laser Altimeter, a laser that times pulses bouncing off the surface | Moon-wide tier (1° plots, about 30 km). Gives slope, roughness and relief, which become the Landing score; also the shaded-relief global basemap. |
| **LOLA South Pole DEM**, 80 m and 20 m (`LDEM_80S_80MPP_ADJ`, `LDEM_80S_20MPP_ADJ`) | NASA GSFC PGDA | Input | The same laser data at much higher resolution, south of 80°S, in south-polar stereographic map coordinates | The terrain skyline: for every 240 m cell we march out to 150 km in 2° compass steps and record the highest angle terrain reaches. Sun or Earth below that angle is blocked. 20 m near the cell, 80 m far away. |
| **LDSM 20 m slope map** (`LDSM_80S_20MPP_ADJ`) | NASA GSFC PGDA | Input | NASA's slope product derived from LOLA | Share of each polar plot under 8°. A plot is safe to land on if at least 25% is. Otherwise it is Off market. |
| **LDEM 80 m hillshade** (`LDEM_80S_80MPP_ADJ_HILL`) | NASA GSFC PGDA | Input (display) | A pre-shaded picture of the polar terrain | The South Pole District basemap image. |
| **IAU / USGS Gazetteer of Planetary Nomenclature** (`planetarynames.wr.usgs.gov`) | IAU, USGS | Input | Official names and positions of lunar features | Landmarks: maria, mountains, valleys, and craters over 20 km. Feeds the Views score ("nearby" list, max 5 within 300 km). Craters over 50 km count as "major". |
| **Apollo, robotic and Artemis III sites** (`pipeline/data/landmarks.csv`) | NASA, other space agencies; hand-curated | Input | Six Apollo landing sites, robotic landers (Chang'e, Chandrayaan-3, others) and the Artemis III candidate regions. Positions are approximate, about ±0.5° | Highest fame weight (1.0) in the Views score, and the +25% price premium within 50 km of an Apollo or Artemis site. |
| **LOLA illumination maps** (`AVGVISIB_85S_060M`, `…_EARTH`, `LPSR_85S_060M`) | NASA GSFC PGDA (Mazarico et al.) | Check | NASA's own maps, at 60 m, of how often each polar spot sees the Sun and the Earth, plus a map of permanently shadowed regions | We compare our sunlit and Earth-visible fractions with them across 78,464 polar plots. Sun: r = 0.987. Earth: r = 0.957. |
| **LRO Diviner** (`lro_diviner_derived1` polar maps, PDS) | NASA / UCLA, hosted by PDS Geosciences | Check | A thermal radiometer on LRO that measures real surface temperature | We compare our modelled temperatures with it. Shadowed craters agree (our 40 K vs about 43 K). Sunlit sites do not (we model an equilibrium maximum, Diviner publishes local-time averages), so the app labels temperatures as modelled. |

## 2. Models and constants we chose (not external data)

| Item | Where | What it is |
|---|---|---|
| Moon radius 1,737,400 m | `config/lunar-listings.yaml` | LOLA's reference sphere |
| Panel, load, battery | `power:` in config | 10 m² Sun-tracking panel at 30% efficiency, 500 W load, 150 Wh/kg batteries: assumed values (Q-P6) |
| Thermal model | `thermal:` | Equilibrium temperature, albedo 0.12, emissivity 0.95; night floors of 95 K Moon-wide, 50 K at the pole, 40 K in shadowed craters |
| Score weights | `weights:` | Landing 30%, Sun 25%, Signal 20%, Comfort 15%, Views 10%, Ice 0% |
| Price | `price:` | $5,000 × e^(6.9 × viability / 100) × (1 + premiums) × scarcity. $5,000 and 6.9 are our choices. Nobody can own the Moon (Outer Space Treaty, 1967), so there is no real market to calibrate to |
| Earth contact rule | `comms:` | Earth must be at least 1° above the local skyline (`terrain_margin`) |
| Analysis year | `analysis:` | 2028, hourly |

## 3. Software

| Where | Tools | Used for |
|---|---|---|
| Pipeline (`pipeline/`) | Python 3.11+, NumPy, Numba, SciPy, pandas, rasterio (GDAL), Pillow, Matplotlib, pyshp, PyYAML, requests; pytest and ruff for tests and lint | All the science, run offline: Horizons parsing, terrain skylines (Numba), visibility statistics, scoring, pricing, export of static data files |
| App (`app/`) | React 18, TypeScript, Vite, deck.gl 9, zustand, recharts, react-window; vitest and Playwright for tests | The listings site. It reads the pipeline's static files in `app/public/data/` and makes no live API calls, so it works offline in demo mode |
| Presentation | A Claude Slides artifact, Google Fonts (Space Grotesk, Inter) | The 7-slide deck |

## 4. Not used

- **NASA Moon Trek and Quickmap** appear in the original spec as an optional cross-check, but nothing in the code uses them. `docs/presentation.md` lists Moon Trek in its project-page draft; that line is out of date. Both basemaps are our own shaded-relief images made from LOLA data.
- **No ice measurement.** "Ice" is the distance to the nearest permanently shadowed region (never sunlit in our 2028 model), a proxy. It drives the Ice score and the Ice depot Home type, not the price.

## 5. Limits worth saying out loud

- The premise and prices are fictional; the data and geometry are real.
- Screening-level analysis, not mission certification. Boulder-scale hazards are not resolved.
- The Moon-wide tier assumes a flat horizon (a 1° plot is about 30 km across); only the South Pole District uses real skylines.
- Earth contact covers 2028 only; NASA's maps integrate 2016-2020.
