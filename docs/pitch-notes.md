# Lunar Listings: 2-minute pitch notes

Companion to the 7-slide deck ("Lunar Listings – Space Apps 2026", a Slides artifact; export to PowerPoint or Google Slides
from its Share menu). The same text is in each slide's speaker notes. About 280 words, 2:00 at a calm pace.

**Roles:** one person talks, one drives the app (offline demo mode, `?demo=1`). Keep the backup recording open in another tab.

| Time | Slide | Say |
|---|---|---|
| 0:00 | 1 · Title | "Imagine the UN started selling plots on the Moon. Where would you buy? We built the listings site, and every price on it is computed from real NASA data." |
| 0:12 | 2 · Problem | "The challenge asks for a way to compare landing sites and dates by seeing where the Sun and Earth sit against the horizon. At the south pole, a few kilometers or a few days flip a site from sunlit and in contact with Earth to dark and cut off. The data exists, but it isn't approachable." |
| 0:27 | 3 · Idea | "Everyone knows how to browse homes, so we turned lunar science into listings. A plot's beds and baths are its sunlight and Earth contact. The Zestimate becomes the Moonstimate. Plots that aren't safe to land on are simply off the market." |
| 0:42 | 4 · How it works | "We ask JPL Horizons where the Sun and Earth are every hour of 2028, and we use LRO LOLA terrain. At the south pole we trace the real skyline around every cell, because that's what makes or breaks a site. Scores for safety, power, comms, temperature, landmarks and ice become a viability number, and that becomes the price." |
| 1:00 | 5 · What you can do | **Switch to the live demo (about 25 s).** "A far-side plot is the cheapest on the market, about ten thousand dollars, with no Earth contact. Near-side plots with Earth always in view reach eight hundred thousand. The top South Pole rim tops a million: sunlit 80% of the year, with ice two kilometers away." Click: Far-side bargain, then Shackleton rim and its 3D Tour. |
| 1:30 | 6 · Why trust it | "It's playful on the surface and checked underneath. Our Sun and Earth geometry matches JPL Horizons to six thousandths of a degree. Our polar lighting correlates 0.99 with NASA's own illumination maps. And we say what we don't model: this is screening, not mission certification." |
| 1:45 | 7 · Impact and team | "It makes lunar landing science something anyone can browse: students, the curious, future space entrepreneurs. Next: an AI realtor, plot comparison, rover routes, lunar towns. Try it at the link. We're [team]. Thank you." |

## Numbers on the slides, and where they come from

All are from the committed data in `app/public/data/` or `docs/validation.md`. Re-check them if the pipeline is rerun.

| Claim | Value | Source |
|---|---|---|
| Plots | 64,800 Moon-wide; 78,464 polar | `cols.json` row counts |
| Cheapest on-market plot | $10.6K, far side, 0% Earth contact | `global/cols.bin` |
| Near-side example | $843K at 0.5°N 23.5°E, Earth in view 100% | `global/cols.bin` |
| Top South Pole plot | $1.09M, 80% sunlit, 87% Earth, ice 2.2 km | `polar/cols.bin` |
| Horizons check | worst error 0.006° (pass: 0.1°) | `docs/validation.md` (EPH-3) |
| LOLA illumination agreement | r = 0.987 | `docs/validation.md` |
| Slope vs NASA LDSM | r = 1.000 | `docs/validation.md` |

## If you run long

Cut slide 4's detail to one sentence, and shorten the demo to the far-side plot plus the Shackleton 3D Tour.
If the live app fails, play the recorded demo (see `docs/demo-video-script.md`).

## Likely questions

- **Is this real?** The premise is fictional (under the 1967 Outer Space Treaty nobody can own the Moon). The science and data are real; prices are model outputs from stated assumptions in `config/lunar-listings.yaml`.
- **How do you handle terrain?** At the South Pole we ray-march the DEM (20 m near, 80 m far) at 2° azimuth steps to get a skyline for every cell, then test the Sun and Earth against it each hour.
- **How accurate?** Sun/Earth directions are checked against Horizons; polar lighting against NASA's LOLA illumination maps; slopes against NASA's LDSM; shadowed temperatures against LRO Diviner. Limits: screening level, boulders not resolved, temperatures are an equilibrium model.
- **Why is the Moon-wide tier flat?** It uses zero terrain for lighting (a 1° plot is about 30 km); only the pole uses real skylines.

## Presenter cheat sheet: if someone asks

Same text as the deck's speaker notes (the "IF ASKED" parts). The pipeline and `config/lunar-listings.yaml` are the source of truth.

### Resources used and how (slide 4)

JPL HORIZONS (NASA JPL ephemeris service). We ask it for the direction and distance of the Sun and Earth as seen from the Moon, every hour of 2028 (366 days x 24 = 8,784 steps), and convert that to elevation and azimuth at any plot. Elevation above 0 degrees means the body is above a flat horizon. The Sun's distance also sets how bright it is (inverse square) and how big it looks. It is both an input and our ground truth: we check our own geometry against fresh Horizons queries.

LRO LOLA (Lunar Orbiter Laser Altimeter). A laser on the Lunar Reconnaissance Orbiter that times pulses bouncing off the surface, so it measures height. We use three products. (1) The global 118 m map from USGS, for Moon-wide plots (1 degree each, about 30 km). (2) The 80 m and 20 m South Pole maps from NASA GSFC PGDA, for the pole. Heights give slope, roughness and relief, which become the Landing score.

THE SKYLINE. For every 240 m polar cell we march outward up to 150 km in 2 degree compass steps and record the highest angle the terrain reaches, allowing for the Moon's curvature. That list is the cell's horizon. The Sun counts as lit only if more than half its disk is above the horizon; Earth counts as visible only if it is at least 1 degree above the horizon. The Moon-wide tier assumes a flat horizon because a 30 km plot averages the terrain out.

LDSM. NASA's 20 m slope map made from LOLA. A plot is safe to land if at least 25 percent of its area is under 8 degrees. If not, it is Off market and its viability is capped at 10.

IAU GAZETTEER + APOLLO/ARTEMIS. Official names (maria, mountains, valleys, craters over 20 km; major means over 50 km) plus the six Apollo sites and the Artemis III regions. They feed the Views score and the Apollo premium.

CHECKS, NOT INPUTS. LOLA illumination maps (Mazarico et al.) are NASA's own map of how often each polar spot is lit; we compare against them. LRO Diviner is a thermal radiometer that measures real surface temperature; we compare shadowed craters against it.

ICE. We have no ice measurement. Ice is the distance to the nearest permanently shadowed region (never sunlit in our 2028 model). It only drives the Ice score and the Ice depot Home type, not the price.

COUNTS. 64,800 Moon-wide plots (1 degree grid) and 78,464 South Pole District plots (960 m).

### How each score is built (slide 3)

LANDING (weight 30%). 100 minus a hazard score: the average of three 0-1 numbers, the 90th-percentile slope, the surface roughness and the local relief of the plot, each scaled against a fixed range. Steep, rough, uneven ground scores low.

SUN (weight 25%). Model a 10 square metre Sun-tracking solar panel at 30 percent efficiency. Average its output over the year, subtract a 500 W constant load, and scale against 3,000 W of net power. Then divide by (1 + battery mass / 2,000 kg), where battery mass is 500 W x the longest night in hours / 150 Wh per kg. So a 14-day night (336 h) needs about 1,100 kg of battery and cuts the score to about 64 percent. Long nights are punished.

SIGNAL (weight 20%). Fraction of the year Earth is at least 1 degree above the local skyline, times a penalty for the longest blackout: 1 / (1 + (hours / 120)^2). A 120 hour (5 day) blackout halves it.

COMFORT (weight 15%). Temperature from a simple equilibrium model: T = ((1 - 0.12) x sunlight flux / (0.95 x sigma))^(1/4), with floors of 95 K at night Moon-wide, 50 K at the pole, 40 K in shadowed craters. Score is high when it is not too cold (40 to 120 K scale) and the swing from coldest to hottest is small (100 to 300 K scale).

VIEWS (weight 10%). The best of: fame x e^(-distance / 100 km) over landmarks within 300 km. Fame is 1.0 for Apollo and Artemis sites, 0.6 for major craters, 0.3 for others.

ICE (weight 0%, polar only). 1 minus distance to the nearest shadowed region / 50 km. Not in the price. It drives the Ice depot match.

VIABILITY = the weighted average of the five scores above. This is the number the price is built from.

HOME TYPES re-weight the same scores and add a gate. Lander pad: Landing 0.4, Sun 0.35, longest night 48 h or less over a 14-day stay. Habitat: Signal 0.35, Comfort 0.25, longest blackout 168 h or less over 90 days. Solar farm: Sun 0.6, at least 40 percent safe area and 60 percent sunlit. Ice depot: Ice 0.45, Sun 0.25, ice within 2 km. The '% match' is the weighted average of those scores.

### How the price is determined (slide 5)

price = $5,000 x e^(6.9 x viability / 100) x (1 + premiums) x scarcity

- Viability is the 0-100 weighted score (Landing 30, Sun 25, Signal 20, Comfort 15, Views 10).
- The exponential means every +10 viability roughly DOUBLES the price (e^0.69 = 2). Viability 0 is about $5K, 50 is about $157K, 100 is about $5M.
- Premiums add up: +25 percent within 50 km of an Apollo or Artemis site; +50 percent for Peak of light (polar plot sunlit 70 percent of the year or more).
- Scarcity: x1.3 for the top 2 percent of plots by viability.
- Unsafe plots are capped at viability 10 and shown Off market.
- Displayed as a range: plus or minus 25 percent Moon-wide, plus or minus 10 percent at the pole (the pole is modelled in more detail, so less uncertain). Shown to 3 significant figures.
- $5,000 and 6.9 are our choices, not market data. Nobody can own the Moon (Outer Space Treaty, 1967), so there is nothing real to calibrate to. They set the scale; the ranking is what the science drives.

WHY THE THREE EXAMPLES DIFFER
- Far side, $10.6K: working back from the price, viability is about 11. Earth is never visible (Signal = 0, 20 percent of the score lost) and nights last two weeks (Sun score is cut by the battery term).
- Near side, $843K at 0.5N 23.5E: Earth always in view (100 percent), and these coordinates are the Apollo 11 site, so it gets the +25 percent Apollo premium. Working back, viability is about 70.
- Top pole rim, $1.09M: 80 percent sunlit, 87 percent Earth, ice 2.2 km away. At 70 percent sunlit or more it counts as Peak of light (+50 percent premium). The listing's 'Why this price' panel in the app shows the exact breakdown.

Back-calculated viability figures are estimates from the price; the app is the source of truth.

RENT is built (RENT_RATIO 0.006 x the price for the stay's viability) but switched off in this build, so do not demo it.

### What the validation numbers mean (slide 6)

0.006 DEGREES (JPL Horizons). We compared our Sun and Earth elevations with Horizons' own answers at 7 sites (near side, limb, mid-latitude, three polar sites incl. the pole), 4 dates, 48 hours each. The worst error was 0.0058 degrees. The Sun is about 0.53 degrees wide, so that is about 1 percent of its width. The requirement was 0.1 degrees at the pole.

r = 0.987 (LOLA illumination). Across 78,464 polar plots, our sunlit fraction vs NASA's LOLA-derived map. r is the correlation: 1.0 is perfect agreement in pattern. Bias is -0.004 (we read 0.4 percentage points lower) and 99 percent of plots are within 10 percentage points. Earth contact agrees less well: r = 0.957, we read 6.6 points lower, 75 percent within 10 points. That is expected: we need Earth 1 degree clear of the horizon and cover only 2028, while NASA integrates 2016-2020.

r = 1.000 (slope). Our own slope calculation vs NASA's LDSM on 102,400 plots: mean error 0.04 degrees. It shows our DEM handling is correct. The shipped data uses NASA's product.

DIVINER (be honest about this one). Permanently shadowed craters: our 40 K floor vs Diviner's median of about 43 K, a good match. Sunlit sites do NOT match well: our annual maximum is far higher than Diviner's local-time averages (bias about +120 K, r about 0.12) because ours is a flat-surface equilibrium model at peak Sun, and Diviner's maps average over season and sun angle. Our 95 K night floor is also above Diviner's median of about 65 K. The app labels temperatures as modelled, and Comfort is only 15 percent of viability.

LIMITS. Screening level, not mission certification. Boulder-scale hazards are not resolved. Temperatures are modelled, not measured. Prices are model outputs from stated assumptions.
