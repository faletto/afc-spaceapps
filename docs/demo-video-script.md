# Lunar Listings: demo video script

Two cuts from one capture session: the **30-second video** (the official Space Apps demo link) and a **90-second walkthrough**
(for the project page and as the live-pitch backup).

Record in demo mode: `http://localhost:4173/?demo=1` (production build, offline). Window 1920×1080, browser zoom 100%.
Use `?present=1&demo=1` for larger type. Show the cursor so viewers see a real app. Rent is switched off in this build,
so do not show or mention it.

## 30-second cut

| Time | On screen | Caption | Narration |
|---|---|---|---|
| 0:00–0:04 | Title card, then the Moon-wide map with price markers | **LUNAR LISTINGS** · *The UN is selling the Moon.* | "The UN just started selling the Moon." |
| 0:04–0:09 | Click **Earth contact overlay**; the near side lights up, the far side goes dark | *Every price from real NASA data* | "Lunar Listings prices every plot from real NASA data: sunlight, Earth contact, temperature and terrain." |
| 0:09–0:14 | Click **Far-side bargain** → listing opens | *Far side: about $10K · no Earth contact* | "The far side? Cheap. No signal home, and two-week nights." |
| 0:14–0:25 | Click **Sunlight at the pole**, then **Shackleton rim + 3D Tour**; the Sun skims the jagged horizon | *South Pole: terrain decides* | "The south pole is the Moon's Manhattan. A crater rim gets near-endless sun; a few kilometers away it is permanent night." |
| 0:25–0:30 | Logo card | *NASA JPL Horizons · LRO LOLA · Diviner* · *Find your place on the Moon.* | "Lunar Listings. Find your place on the Moon." |

Narration is about 65 words. No shot shorter than 2 s.

## 90-second walkthrough

| Time | On screen | Narration |
|---|---|---|
| 0:00–0:10 | Moon-wide map, price markers, zoom in until price pills appear | "This is Lunar Listings: the Moon as a listings site. Every plot has a price, the Moonstimate, computed from NASA data." |
| 0:10–0:22 | Overlays: Sunlight, then Earth contact | "Switch overlays to see why prices differ: how much of 2028 a plot is lit, and how often Earth is above its horizon." |
| 0:22–0:35 | **Far-side bargain**: listing, scores, facts line, "why this price" | "The far side is the bargain: no Earth contact at all. The listing tells you why: the facts, the scores, and a plain-language reason for the price." |
| 0:35–0:45 | Back, set a **Home type** (e.g. Lander pad), show "% match" and the sort | "Pick what you want to build: a lander pad, a habitat, a solar farm, an ice depot. Plots are ranked by how well they fit." |
| 0:45–0:55 | Switch to **South Pole District**; show the sunlight overlay (rims glow, craters black) | "Switch to the South Pole District, where the terrain decides everything. Bright rims, permanently dark craters." |
| 0:55–1:15 | **Shackleton rim + 3D Tour**: drag the time slider; Sun and Earth move over the skyline | "Open a rim. The 3D Tour draws the real skyline from NASA laser-altimeter data, with the Sun and Earth moving across it. Drag the date and watch the light change." |
| 1:15–1:25 | Open **About** → Formulas and Validation | "Every formula and source is in the app, and our geometry is checked against JPL Horizons to six thousandths of a degree." |
| 1:25–1:30 | Logo card | "Lunar Listings. Fictional premise, real science." |

## Numbers (verify at capture time, the data may be regenerated)

| Shot | Value in the current data |
|---|---|
| Cheapest on-market far-side plot | $10.6K, 0% Earth contact |
| Near-side example (0.5°N, 23.5°E) | $843K, Earth 100% |
| Top South Pole plot | $1.09M, 80% sunlit, 87% Earth, ice 2.2 km |
| Horizons check | worst error 0.006° |

If a number on screen differs from a caption, change the caption: the app is the source of truth.

## Capture checklist

1. `cd app && npm run build && npm run preview`, open `http://localhost:4173/?demo=1`, wait for the map to finish loading.
2. Record at 1920×1080, 30 fps, system audio off; record narration separately and mix at the edit.
3. Burn in captions at least 48 px high, on screen for 1.5 s or more.
4. Music bed low; no shot under 2 s; show clicks.
5. Export 1080p MP4; upload to YouTube (unlisted or public) and keep a copy in Drive.

**Backup plan:** if the 3D Tour is slow on the recording machine, record it on a machine with a GPU, or in a separate
take at `?present=1`, and cut it in.
