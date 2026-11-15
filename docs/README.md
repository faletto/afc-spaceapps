# Lunar Listings — project docs

NASA Space Apps Challenge 2026 · Lunar Landing Site Navigator · Team afc-spaceapps

**Fictional premise, real science:** the UN is selling the Moon, and Lunar Listings is the Zillow-style listings site. Every plot's price (the Moonstimate) is computed from NASA data.

Start with the repo-root [`README.md`](../README.md) (overview, commands), then [`app/README.md`](../app/README.md) and [`pipeline/README.md`](../pipeline/README.md).

## Canonical documents (v2.2, final)

| Document | What it is |
|---|---|
| [`requirements.md`](requirements.md) | **Source of truth**: what to build and how well (v2.2 final) |
| [`milestones.md`](milestones.md) | Build plan M0–M8, exit criteria, time split, risks |
| [`presentation.md`](presentation.md) | 30-second video script, 7-slide outline, live-pitch flow, project-page draft, capture checklist |
| [`resources.md`](resources.md) | Every dataset, model and tool we use, what it is, and how we use it |
| [`technical-spec.md`](technical-spec.md) | How to build it: architecture, algorithms, data formats, frontend, tests |
| [`build-plan.md`](build-plan.md) | Task-by-task plan for the 48 h event: owners, hours, dependencies, done-when checks, cut list |
| [`agents/`](agents/) | **Two-agent build:** `PLAN.md` (who does what, git workflow, handoffs), `KICKOFF.md` (prompts to paste), `pipeline-log.md` / `app-log.md` (each agent's memory + messages), `answers.md` (human decisions), `CONTRACT.md` (data contract version) |
| [`plan-review.md`](plan-review.md) | Original review of the team's first plan (background only) |

Word exports of the requirements, milestones and presentation plan are in `../Claude outputs/`. They're exports: edit the markdown here, then regenerate.

The final 7-slide deck is [`lunar-listings-deck.pptx`](lunar-listings-deck.pptx) (offline in PowerPoint or Keynote; import into Google Slides for online). Rebuild notes: it mirrors the "Lunar Listings – Space Apps 2026" Slides artifact.

## Figures (`img/`)

| File | Use |
|---|---|
| `architecture.png` | Data → pipeline → web app (slide 4, README) |
| `personas.png` | Who it's for and the user flow |
| `horizons.png` | Roadmap: today → next → vision (slide 7) |
| `roadmap.png` | Build plan timeline |
| `concept-mockup.png` | Concept UI mockup (illustrative values; replace with real screenshots) |
| `concept-skyview.png` | Concept 3D Tour (illustrative; replace with a real capture) |

## History

- `archive/`: earlier spec versions (v0.4, v1.0, v2.0, v2.1) and milestones/presentation versions.
- The team's original planning notes stay at the repo root: `../Zillow on the moon planning.md`.
- The team's v2.1 spec was moved here as `requirements.md` (git history kept) and updated to v2.2.
