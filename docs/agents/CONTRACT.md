# Data contract (pipeline → app)

*Single writer: **Pipeline Claude**. App Claude checks this and `app/public/data/manifest.json` → `contract_version` at every session start.*

## Current version: **v1** (H0, stub data)

Definition: `docs/technical-spec.md` §5 (files, columnar schema, tile layout) + `config.json` keys (spec §4) + golden-vector schema (`pipeline/tests/golden/`, from v2).

## Change log
| Version | Date | Handoff | Change | Files regenerated | Breaking? |
|---|---|---|---|---|---|
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
