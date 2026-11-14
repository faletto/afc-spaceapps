# Data contract (pipeline → app)

*Single writer: **Pipeline Claude**. App Claude checks this and `app/public/data/manifest.json` → `contract_version` at every session start.*

## Current version: **v2** (H3 real Moon-wide; H4 real polar, additive — still v2)

Definition: `docs/technical-spec.md` §5 (files, columnar schema, tile layout) + `config.json` keys (spec §4) + golden-vector schema (`pipeline/tests/golden/`, from v2).

## Change log
| Version | Date | Handoff | Change | Files regenerated | Breaking? |
|---|---|---|---|---|---|
| v2 | 14 Nov | H3 | Real `global/` tier. `cols.json.land_types` = [highlands, mare, far_side, crater_rim, crater_floor, psr, peak_of_light] (read it from cols.json, don't hard-code). `manifest.tiers` = {global: real, polar: stub}; `detail/*.json` real fields (id, land_type, slope_p90_deg, roughness_m, relief_m, safe_area_frac, landing_safe, energy_wh_m2_day, longest_light_h, mean_earth_el_deg, temp_mean_k, monthly_sunlit_pct[12], monthly_earth_pct[12], nearby[]); overlays are 1440×720 RGBA, extent [-180,-90,180,90]; basemap = hillshade 8192×4096; landmarks.json = 1,454 IAU/curated; golden vectors `pipeline/tests/golden/golden_v1.json` | global/*, landmarks.json, config.json, manifest | No (additive; enum read from cols.json) |
| v1 | 14 Nov | H0 | Spec §5 as written, made concrete (see below); `manifest.contract_version = 1`, `stub: true` | all (stub) | — |
| v0 | 14 Nov | — | Draft | — | — |

## Rules
- Every breaking change bumps the version **in the same commit** as the updated `stub.py` output, golden vectors and the `manifest.json` field.
- Additive changes (new optional column, new file) bump the minor note but not the version; App may ignore them.
- App requests changes via `## Requests to Pipeline Claude` in `app-log.md`.

## v1 concrete details (where spec §5 was silent) — ASSUMED, tell Pipeline if the app needs otherwise
- **Rows are sorted by `tile`**; `row_in_tile` = order within the tile. `tile = ty*16 + tx` (16×16). Files: `<tier>/detail/<tx>_<ty>.json`, `polar/horizon/<tx>_<ty>.bin`. **Empty tiles have no file** (polar corners).
- **App must derive tiles from `cols.json` `bounds` + `projection` + `tiles_per_axis`, not from the formulas below** (the real polar projection/crop will replace the stub's without a version bump).
- **Global tile bounds (stub):** `tx = floor((lon+180)/22.5)`, `ty = floor((lat+90)/11.25)`. **Polar:** square `[-rmax, rmax]²` split 16×16, `rmax = R·5°` (azimuthal-equidistant stand-in; x,y in metres, y up; stub only — real projection stated at H3/H4).
- **`cols.json`**: `{rows, columns:[{name,dtype,offset,scale}], land_types[], flags{name:bit}, tiles_per_axis}`. Real value = stored × `scale`. Each column 4-byte aligned, little-endian, one contiguous array per column. `ice_km10` 65535 = n/a.
- **Flags bits:** off_market 0, hot_property 1, price_cut 2, earth_view 3, featured 4, tier_polar 15.
- **`ephemeris.bin`:** float32 LE, concatenated: `sun_xyz[8784×3]`, `earth_xyz[8784×3]`, `earth_dist_m[8784]`, `tsi[8784]`; unit vectors in the Moon-fixed frame; hour 0 = 2028-01-01T00:00Z.
- **Horizon tiles:** `uint8`, 180 az samples (2° steps) per plot, elevation_deg = v × `unit_deg` + `offset_deg` (manifest `horizon`; stub: 0.25, −10 so negative horizons fit; values may be retuned without a version bump).
- **Detail JSON:** array of records `{row, name, blurb, sunlit_monthly[12]}` in stub (real fields from req §10 arrive at H3; additive).
- **Overlays:** RGBA PNG per tier + `<name>.json` legend `{name,label,unit,min,max,ramp,size}`; names: viability, sunlit, earth, temperature, safety, ice. **Basemap:** `<tier>/basemap.jpg`.
- **`config.json`** = validated YAML + `computed.scarcity_viability_cutoff` (stub: 85).
- Stub values are fake (price = 5000·(1+6.9·v/100) is a placeholder); counts: global 64,800, polar ≈ 78k (not 91k).
- **Monthly arrays** (`sunlit`/`earth`) are fractions 0–1 in the pipeline; the columnar/detail exports convert to percent where the schema says `_pct`.
- **Polar azimuth/lon:** `geometry.py` measures azimuth from the lon=0 meridian at the pole; the polar export converts stereographic x/y to lon via `atan2(x, y)` consistently with that (to be fixed in P4; additive).
- **v2 notes:** global rows are sorted by tile; `x,y` = lon,lat (deg). `ice_km10` = 65535 (n/a) for the whole global tier. `s_ice` = 0. Flags: hot_property = viability ≥ P95 (all plots); earth_view = limb (80°≤|lon|≤100°) with earth_frac ≥ 0.95; off_market = not landing_safe; price_cut is Rent-only (client side). `bw_*` = best-window minimum hours (lander: longest night in a 14-day stay; habitat: longest blackout in a 90-day stay) and start day-of-year (a window must fit in the year). Moon-wide viability tops out ≈ 65 (see Q-P6): price range ≈ $8K–$730K.
- **Prices:** landmark premium (Apollo) is applied where `landmark_score > 0.5` (ASSUMED rule); price = BASE·exp(k·v/100)·(1+premium)·scarcity (scarcity cutoff in `config.json computed`).

## H4 notes (polar tier real; additive, contract stays v2)
- **Projection** (in `polar/cols.json` `projection` + `bounds` [-153600,-153600,153600,153600]): south polar stereographic, sphere R=1,737,400 m, k0=1, `x = ρ sin(lon)`, `y = ρ cos(lon)`, ρ = 2R·tan(45°+lat/2), lon east-positive, +y up. Azimuth/bearing α (0=N, 90=E) at a site maps to map direction (sin(lon+α), cos(lon+α)). Derive tile indices from `bounds` (16×16, ty increases with y); empty tiles have no file.
- **Horizon tiles** (`polar/horizon/<tx>_<ty>.bin`): 180 uint8 per plot (2° steps from local north), rows in `row_in_tile` order; **elevation_deg = v × 0.16 − 6.0** (manifest `horizon` = {unit_deg 0.16, offset_deg −6, az_count 180}); v=0 clamps ≤ −6°, v=255 ≥ 34.8°. It is the horizon at the plot's **best cell** (also the cell whose light/Earth/temperature facts are shown; `detail.best_cell_xy`).
- Polar plots: 78,464 (plot centre at lat ≤ −85°, 960 m plots, 240 m cells). Plot area facts (slope/roughness/relief/safe fraction) are whole-plot; light/comms/temperature facts from the best cell; `ice_km10` = distance to nearest PSR cell (cell sunlit < 1%) in 0.1 km. Plot IDs `SP-<row>-<col>` in detail (plot grid 320×320, row 0 at +y).
- **Scarcity cutoff and the hot-property P95 are computed over global ∪ polar** and in `config.json computed.scarcity_viability_cutoff`; global prices/flags regenerated at H4 (global prices changed vs H3).
- **Home-type gates** (human-approved 14 Nov): lander ≤ 48 h (longest night, `bw_lander_h`), habitat ≤ 168 h (longest blackout, `bw_habitat_h`), solar farm safe_area_frac ≥ 0.4 & sunlit_frac ≥ 0.6, ice depot ice_km ≤ 2 (polar only). Polar counts: 25,715 / 397 / 56 / 36,233 (landable plots).
- `config.json` `safety.roughness_range_m` / `relief_range_m` are now [0,600] / [0,4000] (Q-P3).
- Golden vectors gained `horizon_quantisation`. Known limits: Moon-wide `s_power` ≈ 0 (Q-P6, open); polar `s_power` max ≈ 0.26 under the spec's dark penalty (h50 = 120 h), ranking still puts Connecting Ridge / Malapert in the top 0.3%.
- **Land type (polar tier):** the `|lon| > 90° → far_side` rule is skipped for polar plots (meaningless within 5° of the pole); mare/highland split uses the **global** plot median elevation − 1 km. **Price premium:** `apollo_premium` (+25%) within `apollo_radius_km` (50 km) of an Apollo/Artemis landmark, plus `peak_light_premium` (+50%) on Peak-of-light plots (additive in `(1 + premium)`).
