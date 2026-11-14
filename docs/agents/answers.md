# Answers & decisions (humans only)

*Single writer: **humans**. Agents read this at every session start. Answer by question ID from the agent logs (`Q-P#`, `Q-A#`). Newest first.*

## Decisions already made (14 Nov)
| ID | Decision |
|---|---|
| D-1 | Stack: Python 3.11 pipeline (NumPy, Numba, rasterio, SciPy); React + TypeScript + Vite + deck.gl app; static hosting (GitHub Pages) |
| D-2 | Earth contact = Earth ≥ 1° above local terrain horizon (`terrain_margin`); absolute 5° kept as config option |
| D-3 | Analysis year 2028 (8,784 hourly steps) |
| D-4 | Price: BASE $5,000, k 6.9; range ±25% Moon-wide, ±10% polar; RENT_RATIO 0.006 |
| D-5 | Grids: 1° Moon-wide; polar 240 m cells, 960 m plots, core area 85–90°S |
| D-6 | Product name: "Lunar Listings" (working name) |

## Pending (agents: use the default and mark ASSUMED until answered)
| ID | Question | Default |
|---|---|---|
| — | Home-type gate values | Calibrate in P3 so each type returns ≥ 50 polar plots; humans approve |
| — | Commit real data to git or publish as a Release? | Commit if < 50 MB |

## Answers
<!-- Q-ID · answer · date -->
