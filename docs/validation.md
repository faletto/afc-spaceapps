# Validation: ephemeris vs JPL Horizons (EPH-3)

Our Sun/Earth elevations vs direct Horizons topocentric queries (`CENTER='coord@301'`, `QUANTITIES='4'`), 7 sites × 4 dates × 48 h. Pass: polar sites ≤ 0.1°, Moon-wide sites ≤ 1.0°. **Result: PASS** (worst elevation error 0.0058°).

| Site | Target | Max elevation error (°) over 4 dates | Max azimuth error (°, target above horizon) |
|---|---|---|---|
| Near side (0°, 0°) | Sun | 0.0007 | n/a (pole / below horizon) |
| Near side (0°, 0°) | Earth | 0.0053 | 0.047 |
| Near side (30°N, 20°E) | Sun | 0.0005 | 0.000 |
| Near side (30°N, 20°E) | Earth | 0.0034 | 0.007 |
| Limb (0°, 90°E) | Sun | 0.0005 | 0.000 |
| Limb (0°, 90°E) | Earth | 0.0058 | 0.000 |
| Mid-lat south (60°S, 150°W) | Sun | 0.0008 | 0.000 |
| Mid-lat south (60°S, 150°W) | Earth | 0.0019 | n/a (pole / below horizon) |
| South polar (85°S, 30°W) | Sun | 0.0007 | 0.000 |
| South polar (85°S, 30°W) | Earth | 0.0005 | 0.006 |
| South polar (89.7°S, 45°E) | Sun | 0.0007 | 0.000 |
| South polar (89.7°S, 45°E) | Earth | 0.0004 | 0.006 |
| South Pole (90°S) | Sun | 0.0007 | n/a (pole / below horizon) |
| South Pole (90°S) | Earth | 0.0005 | n/a (pole / below horizon) |

## Independent cross-checks of the South Pole tier (NASA data)

### Lighting vs LOLA-derived average visibility (PGDA, Mazarico et al.; HOR-2 cross-check)
Our `sunlit_frac`/`earth_frac` at each plot's best cell vs the LOLA 60 m maps averaged over our 240 m cell (78,464 plots).

| Quantity | Pearson r | bias (ours − LOLA) | RMSE | within ±0.10 |
|---|---|---|---|---|
| Sun visible fraction | 0.987 | -0.004 | 0.025 | 99% |
| Earth visible fraction | 0.957 | -0.066 | 0.092 | 75% |

PSR (< 1% sunlit): ours 15.2% of plots, LOLA 13.2%, classification agrees on 98.0%.
Expected differences: our `sunlit` counts the Sun only when more than half of its disk is above the terrain (LOLA counts any illumination, so it reads higher); our Earth contact needs 1° above the horizon and covers only 2028 (LOLA integrates 2016-2020 libration); LOLA's grid is 60 m vs our 240 m cell mean.

### Temperature vs LRO Diviner polar maps (TEMP-4)
Diviner average bolometric brightness temperature in 240 m bins by local time (PDS `lro_diviner_derived1`, summer and winter seasons). Our T1 is an equilibrium model with floors (95 K sunlit, 40 K PSR).

| Comparison | n | Result |
|---|---|---|
| Max temperature (ours annual max vs Diviner max of local-noon bins) | 74,840 | r = 0.12, bias +119 K, RMSE 134 K |
| Night floor at lit sites (>30% sunlit) | 25,327 | ours 50 K vs Diviner median 65 K (10th pct 53 K) |
| PSR plots, max temperature | 11,032 | ours 40 K vs Diviner median 44 K (90th pct 62 K) |

**Reading:** permanently shadowed plots agree (40 K floor vs Diviner ≈ 43 K). For sunlit sites our modelled annual maximum (flat surface at peak Sun elevation) is far above Diviner's local-time-binned averages (bias +119 K, r = 0.12), because the binned maps average over season, sun angle and sub-bin shadowing and so do not capture annual extremes, while T1 ignores terrain-scattered light and subsurface conduction. TEMP-4 is therefore a coarse check: shadowed terrain validates, lit-site maxima and the 95 K night floor (Diviner nights ≈ 65 K) are conservative/modelled values and the app labels temperatures as modelled. The thermal sub-score uses the swing (max − min), so it likely overstates polar swings (Q-P8).

### Slope: our central differences vs NASA's LDSM 20 m slope product
The pipeline uses the LDSM product for slopes and safe-area fractions (spec §3.4). For reference, a plain central-difference slope on the same 20 m DEM agrees with it on the 960 m plot grid as follows (102,400 plots):

| Quantity | Pearson r | bias (own − LDSM) | RMSE |
|---|---|---|---|
| Plot mean slope (deg) | 1.000 | +0.04 | 0.05 |
| Share of area under 8° | 1.000 | -0.002 | 0.006 |

Per-pixel difference: bias +0.04°, RMSE 0.31°. The two agree closely, so the earlier own-slope approximation (Q-P4) was sound; the exported data now uses the NASA product.

