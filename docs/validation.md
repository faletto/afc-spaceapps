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
