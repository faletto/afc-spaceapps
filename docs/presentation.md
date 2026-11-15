# Lunar Listings — Presentation Plan (30-second video + 7 slides)

*NASA Space Apps Challenge 2026 · Team afc-spaceapps · v2.2 (final) · 14 Nov 2026*

*Companion to `docs/requirements.md` v2.2 (final), §11. v2.2 uses the Zillow vocabulary from requirements v2.1: **3D Tour**, **Rent** tab, **Home type**, named scores, badges. Space Apps rules: a Project Demo is either a video of **up to 30 seconds** or a deck of **up to 7 slides including the title**, publicly hosted, in English (or with English subtitles). Judging criteria: **Impact, Creativity, Validity, Relevance, Presentation**. We make both; the video is the primary link.*

> **Update (15 Nov):** the final deck is [`lunar-listings-deck.pptx`](lunar-listings-deck.pptx) (opens offline in PowerPoint or Keynote, online in Google Slides or PowerPoint for the web; speaker notes include how every score and price is determined). Slide 4 is the resources slide. The 7-slide deck, 2-minute notes and demo video script are in [`pitch-notes.md`](pitch-notes.md) and [`demo-video-script.md`](demo-video-script.md), with real numbers. The Rent tab is switched off in the current build, so those versions omit Rent; the tables below are the original plan.

> **Rule for all numbers.** Prices, percentages and before/after values in the final video and slides must come from the running app. Values in this plan and in the draft deck are **illustrative placeholders** until M6 captures the real ones.

---

## 1. The one-line story

**"The UN is selling the Moon. Lunar Listings is the listings site — and every price is computed from real NASA data."**

Three beats:
1. **Hook:** a familiar Zillow-style map, but on the Moon, with prices.
2. **Insight:** why plots differ. Far side: cheap, no Earth contact. South pole: prime real estate, but terrain decides sunlight and darkness. **Timing matters too.**
3. **Trust:** NASA Horizons and LOLA; terrain-aware horizons; validated.

---

## 2. 30-second video

**Format:** 1920×1080, captions burned in, music bed low. Narration is ≈ 70 words at a normal pace. Every shot is a screen capture from the app except the title card.

| Time | Shot (on screen) | On-screen text | Narration | Captured in |
|---|---|---|---|---|
| 0:00–0:03 | Zoom from space onto the Moon; price pills pop onto the map | **LUNAR LISTINGS** · *The UN is selling the Moon.* | "The UN just started selling the Moon." | M3 |
| 0:03–0:08 | Pan across price markers; toggle Sunlight → Earth contact overlays | *Every price from real NASA data* | "Lunar Listings prices every plot from real NASA data: sunlight, Earth contact, temperature and terrain." | M3 |
| 0:08–0:12 | Click a far-side plot → listing: low price, "Earth contact 0%", "longest night 14 days" | *Far side: $XX K · no Earth contact* | "The far side? Cheap. No signal home, two-week nights." | M3 |
| 0:12–0:21 | Jump to the **South Pole District** → sunlight overlay (rims glow, craters black) → open a rim listing (HOT PROPERTY badge, facts line) → **3D Tour**: the Sun skimming a jagged horizon | *South Pole: $X.XM · XX% sun · XX% Earth* | "The south pole is the Moon's Manhattan. Here the terrain decides everything: a crater rim gets near-endless sun, while a few kilometers away it's permanent night." | M4 |
| 0:21–0:26 | Switch to **Rent** → move-in date +2 weeks → rent drops, *Price cut* badge and reason appear | *Move in 2 weeks later → rent ↓ XX%* | "Renting? Move in two weeks later and you'll pay less, because you'd arrive for a five-day night." | M6 |
| 0:26–0:30 | Logo + credits | *Built on NASA JPL Horizons · LRO LOLA · LRO Diviner* · *Find your place on the Moon* · *Fictional premise, real science* | "Lunar Listings. Find your place on the Moon." | M8 |

**Editing notes**
- Keep cuts on the beat; no shot shorter than 2 s.
- Captions are at least 48 px high and stay on screen for 1.5 s or more.
- Show the cursor clicking, so viewers see it's a real app.
- Replace every **XX** with real values from the app (PRS-4).
- Export at 30 fps. Upload to YouTube (unlisted or public) **and** keep a copy in Google Drive.

**Backup plan:** if the Rent tab (M6) isn't ready, give 0:12–0:26 to the south pole and the 3D Tour, and end the narration with "Pick a different crater rim, and the price changes."

**Narration check:** adjust the "five-day night" line to whatever the app actually shows for the captured plot.

---

## 3. Seven-slide deck

The deck is a Slides artifact (downloadable as PowerPoint for Google Slides). Speaker notes are aimed at a live pitch of about 2 minutes.

| # | Slide | Content | Visual | Speaker notes |
|---|---|---|---|---|
| 1 | **Title** | *Lunar Listings* — "The UN is selling the Moon. Here's the listings site." Team, challenge name. | Map with price pills (concept mockup → real screenshot at M8) | "Imagine the UN started selling plots on the Moon. Where would you buy? We built the listings site, and every price comes from real NASA data." |
| 2 | **The problem** | The south pole has extreme lighting and Earth-contact conditions. A few km or a few days change everything. The tools that answer this (Horizons, Moon Trek, Quickmap) are built for specialists. | 3D Tour still: Sun skimming a jagged horizon | "The challenge asks for a way to compare landing sites and dates quickly, by seeing where the Sun and Earth sit relative to the horizon. The data exists. It just isn't approachable." |
| 3 | **Our idea** | Zillow for the Moon. Zestimate → **Moonstimate** · Rent Zestimate → **Rent Moonstimate** · 3 bd · 2 ba · sqft → **82% sun · 61% Earth · 4° · 1 km²** · 3D Home Tour → **3D Tour** of the horizon · Walk Score → **Sun / Signal Score** · Home type → **Lander pad / Habitat / Solar farm / Ice depot** · Off market → **not safe to land**. *Fictional premise, real science.* | Zillow-to-Moon mapping table | "Everyone knows how to browse homes. So we turned lunar science into listings. A plot's beds and baths are its sunlight and Earth contact." |
| 4 | **How it works** | NASA JPL Horizons → Sun and Earth positions. LRO LOLA → terrain, slope, horizons. Pipeline → Systems A–D per plot → Viability → Moonstimate. Two tiers: Moon-wide + **terrain-aware South Pole District**. | Architecture figure | "We query Horizons for where the Sun and Earth are, and LOLA for the terrain. At the pole we trace both against the real skyline, because that's what makes or breaks a site." |
| 5 | **What you can do** | Browse pins and listing cards · open a listing (facts line, named scores) · toggle overlays · take the **3D Tour** at the South Pole · pick a **Home type** · switch to **Rent** and change the move-in date | 3–4 screenshots (concept mockups until M8) | Walk through the demo. Point out the far side vs. south pole contrast, the 3D Tour, and the rent drop. |
| 6 | **Why trust it** | Validated against JPL Horizons (≤ 0.1° at polar sites). Terrain-aware horizons, not a smooth Moon. Sanity checks (equator ≈ 50% sunlit; far side ≈ 0% Earth contact; Shackleton floor ≈ 0% sunlit). Every formula and source shown in the app. Limits stated. | Validation plot (M2) | "It's playful on the surface and rigorous underneath. Every number is reproducible, and we check our geometry against NASA's own ephemeris." |
| 7 | **Impact & next** | Makes lunar landing science approachable for anyone: students, the curious, future space entrepreneurs. Next: ask the realtor (AI), compare plots, rover "commute" routes, plan a lunar town. Links: app · repo · video. | Roadmap figure + QR/link | "Next we'd add an AI realtor, compare plots, and eventually plan whole lunar towns. Try it at the link." |

**Design guidelines for the deck**
- One idea per slide, at most ~25 words of body text.
- Dark "space" background with one accent color for prices. Readable at 24 pt or larger.
- Every screenshot captioned with what it shows.
- A small "Data: NASA JPL Horizons · LRO LOLA" footer on slides 4–6.

---

## 4. Live pitch (if your event has one): about 2 minutes

| Time | Do | Say |
|---|---|---|
| 0:00–0:15 | Slide 1 | Hook: the UN is selling the Moon |
| 0:15–0:30 | Slide 2 | The challenge and the problem |
| 0:30–1:30 | **Live demo in demo mode** (requirements §11 script, steps 1–6) | Far side bargain (Signal Score 0) → Earth-contact overlay → South Pole → rim listing + 3D Tour → Rent, move-in +2 weeks |
| 1:30–1:45 | Slide 6 | Why trust it |
| 1:45–2:00 | Slide 7 | Impact, next steps, link |

One person drives the app and one talks. Demo mode is offline, and the backup recording is open in another tab.

---

## 5. Project page text (draft)

**Lunar Listings — find your place on the Moon**

*Fictional premise:* the UN has started selling the Moon. Lunar Listings is the real-estate site. Every plot has a **Moonstimate** price computed from real NASA data: how much sunlight it gets, how long its nights last, how often it can talk to Earth, how cold it gets, whether it's safe to land, and what's nearby.

*Why:* the challenge asks for an intuitive way to compare lunar landing sites and dates by seeing the Sun and Earth relative to the horizon, to judge power and direct-to-Earth communication. We made that science feel like browsing homes.

*How it works:*
- We query **NASA JPL Horizons** for the sub-solar and sub-Earth points over a year.
- We use **LRO LOLA** elevation data for slope, hazards and, at the south pole, the real terrain horizon around every spot.
- From those we compute sunlight, darkness, Earth contact, temperature and landing safety per plot, combine them into a viability score, and turn that into a price.
- Our Sun/Earth geometry is validated against direct Horizons queries.

*NASA data used:* JPL Horizons API · LRO LOLA global DEM (USGS) and south-polar products (NASA GSFC PGDA) · (cross-checks) LOLA illumination maps and LRO Diviner temperatures. Basemaps are our own shaded relief made from LOLA. Full list: [`resources.md`](resources.md).

*Limits:* fictional premise and prices (under the 1967 Outer Space Treaty nobody can claim the Moon); screening-level analysis, not mission certification; boulder-scale hazards not resolved.

*Next:* AI "ask the realtor", plot comparison, rover routes, lunar town planning.

*Links:* app · repo · video · slides

---

## 6. Capture checklist (by milestone)

| Milestone | Capture | Used in |
|---|---|---|
| M1 | Skeleton UI screenshot | Build record |
| M2 | Validation plot (ours vs. Horizons) | Slide 6 |
| M3 | Global price map; far-side listing; Earth-contact overlay toggle (clip) | Video 0:00–0:12; slides 1, 5 |
| M4 | South Pole sunlight overlay; rim listing; **3D Tour clip** (Sun skimming the horizon) | Video 0:12–0:21; slides 2, 5 |
| M5 | Listing blurb close-up; Home base vs. Ice depot maps | Slide 5 |
| M6 | Rent tab: move-in before/after (clip + numbers, Price cut badge) | Video 0:21–0:26; slide 5 |
| M7 | Novice-test quote; presentation-mode screenshots at 1920×1080 | Slide 7; all |
| M8 | Logo/title card; final cut | Video; deck |
