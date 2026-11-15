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
