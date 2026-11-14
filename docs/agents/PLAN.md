# Agent plan — two Claude Code agents, one repo, two computers

*Owner: humans. Agents read it; they don't edit it (propose changes in your log). v1.0 · 14 Nov 2026.*

This splits `docs/build-plan.md` between **Pipeline Claude** (Python) and **App Claude** (React/TS). The humans keep the presentation track, decisions, the novice test and final merges if they want them.

---

## 1. Why this split

- **Disjoint directories** (`pipeline/`+`config/` vs `app/`) → the two branches almost never conflict.
- **The only coupling is the data contract** (spec §5 + `config.json` + golden vectors), and it's versioned in `docs/agents/CONTRACT.md`.
- **App Claude never waits on the pipeline:** it builds against **stub data** with the real formats from work package P0, then swaps in real data at handoffs.

## 2. Git workflow (two computers)

```
main ────●───────────●────────────●───────────●──────── (integration; tags m0..m8)
          \ H0        \ H3         \ H4         \ H6
pipeline ──●──●──●──●──●──●──●──●──●──●──●──●──●──      (Pipeline Claude)
app      ──●──●──●──●──●──●──●──●──●──●──●──●──●──      (App Claude)
```

- **Your branch:** `pipeline` or `app`. Push after every green task (at least hourly), so the other agent and the humans can see progress.
- **Start of every session:** `git fetch origin`, `git pull --rebase origin <your-branch>`, `git merge origin/main`. **Never** rebase a branch the other agent has merged from.
- **Handoffs (H0, H3, H4, H6):**
  1. Pipeline Claude merges `pipeline` → `main` (`git checkout main && git pull --rebase && git merge --no-ff pipeline && <tests> && git push`).
  2. It bumps `CONTRACT.md`.
  3. It writes a `## Contract/handoffs` entry in its log.
  4. App Claude merges `origin/main` into `app` at its next session start.
- **App → main:** App Claude merges `app` → `main` at the M3, M4, M6 and M7 gates (same procedure) so `main` always has a demoable app.
- **Conflicts:** expected only in files nobody should share. If one happens: stop, don't force-push, record it in your log and ask the human.
- **Push blocked or failing** (no credentials or network)? Commit locally, write `UNPUSHED: <n> commits` in `## Resume here`, and tell the human.
- **Tags** (`m0`…`m8`): the humans tag `main` after checking a gate, or an agent does when asked.

## 3. State tracking across machines

Every log entry records **branch @ short SHA**, and for App Claude also **built against contract vN / main @ SHA**.

`docs/agents/CONTRACT.md` (Pipeline-owned) holds:
- the current **contract version** (`v1` frozen at H0);
- what changed since the last version;
- the stub/golden files that changed with it;
- the `manifest.json` `contract_version` field that App Claude checks at load time (it shows a console warning on mismatch).

**Breaking change rule:** a contract change needs, in the same commit, the bumped version, updated `stub.py` output, updated golden vectors, and a log entry. App Claude adapts at its next session start.

## 4. Work packages

Hours are upper bounds on the 48 h plan (agents may run faster). **H** = handoff. **Read** = spec sections to open (nothing else).

### Pipeline Claude

| WP | Milestone | What | Read | Done when | Hours |
|---|---|---|---|---|---|
| **P0** | M0 | Scaffold `pipeline/` (pyproject, Makefile targets, pytest, ruff); `config/lunar-listings.yaml` + `config.py` (validate, export `config.json`); **`stub.py`**: stub data in the frozen formats (spec §5) incl. `manifest.contract_version = 1`; `CONTRACT.md` v1 | Spec §2, §4, §5; req §10 | `make stub` writes `app/public/data/`; tests green. **→ H0: merge to main** | 0–2 |
| **P1** | M1 | Horizons fetch + parser (longitude-sign line) + `ephemeris.py`; `geometry.py`. *In parallel via subagent:* global terrain (resample, slope, roughness, relief) + polar crop / 240 m cells | Spec §3.1–3.4 | 8,784-row ephemeris committed; geometry + TSI tests green; terrain arrays cached | 2–7 |
| **P2** | M2 | `visibility.py` (Numba) + stats + run lists; `thermal.py`; global plots + SAFE; **`validate.py` (EPH-3)** + sanity suite | Spec §3.6–3.8, §3.12; req §9 | Validation passes (≤ 1° / ≤ 0.1°); `docs/validation.md` + `docs/img/validation.png`; sanity green | 7–13 |
| **P3** | M3 | `land.py`, `scoring.py`, `pricing.py` (BASE 5,000, k 6.9), `best_window` + **gate calibration** (ask humans to approve gate values); `export.py` global; **golden vectors v1** | Spec §3.8–3.11, §5; req §6.8 | `make data` writes real Moon-wide data; golden files committed. **→ H3: merge to main, contract v2 if anything changed** | 13–19 |
| **P4** | M4 | **`horizons.py`** (Numba; plan mode first); terrain-aware polar stats; polar plots, PSR/ice; polar export incl. **horizon tiles for every plot**; HOR-2 cross-check | Spec §3.5–3.6, §3.8, §5 | Cone test ≤ 0.05°; Shackleton floor ≈ 0% sunlit; polar data within budget. **→ H4: merge to main.** If not done by hour 30: ship the simplified-lighting fallback and log it | 19–28 |
| **P5** | M5–M6 | Blurbs + featured plots; rent reference (`pricing.py`) + **rent golden vectors**; TEMP-4 Diviner note; find the demo **before/after number** | Spec §3.10; req §5.6, §6.8 | Rent golden committed; number logged. **→ H6: merge to main** | 28–36 |
| **P6** | M7–M8 | Payload/perf pass; data release decision (commit < 50 MB or Release asset); README pipeline section; bug fixes requested by App | Spec §8; req §8 | Sizes within NFR-4; `make data` reproducible | 36–46 |

### App Claude

| WP | Milestone | What | Read | Done when | Hours |
|---|---|---|---|---|---|
| **A0** | M0 | Scaffold `app/` (Vite, React, TS strict, deck.gl, zustand, react-window, Vitest, Playwright, ESLint); `data/types.ts` from spec §5 | Spec §5, §6.1–6.2 | `npm run dev` shows a canvas; CI job for app | 0–2 |
| **A1** | M1 | Loader (manifest, `cols.bin`, lazy tiles, contract-version check); `MapView` with two tiers; markers (dots ↔ pills by zoom, Off-market grey); results list (virtualized, cap 200); listing shell + fine print. **On stub data (after H0)** | Spec §5, §6.3–6.4; req §5.1–5.3, §5.7 | Click pin/card → listing → back; Playwright smoke green | 2–7 |
| **A2** | M2 | Overlay plumbing + legends + opacity; Web Worker scaffold (filter/sort over typed arrays); glossary tooltips | Spec §6.3–6.4, §6.7; req §5.5 | Stub overlay toggles; worker round-trip; tooltips on facts | 7–13 |
| **A3** | M3 | Merge H3; real Moon-wide data; facts line, why line, filters, sorts; **e2e "Buy price never changes with UI state"** | Req §5.2–5.4, §9 | 64,800 plots smooth; filter < 200 ms; e2e green. **→ merge app to main at M3** | 13–19 |
| **A4** | M4 | `science/*.ts` mirror (geometry, visibility) + **parity tests vs golden**; merge H4; South Pole tier; **3D Tour** (plan mode first) | Spec §3.3, §3.6, §6.5, §7 | Parity green; tour for any polar plot; countdown matches golden. **→ merge app to main at M4 (MVP)** | 19–28 |
| **A5** | M5 | Home type + match % + Best-match sort; named scores; badges; price range; blurb; nearby; land-type filter; "Plots for you"; OV-8, OV-11 | Req §5.3–5.5, §6.8 (named scores, home types) | Each type returns results; prices unchanged | 28–33 |
| **A6** | M6 | `rent.ts` + parity vs rent golden (after H6); Buy/Rent tabs; move-in/stay; rent history; time slider; OV-7 | Spec §3.10, §6.4; req §5.6 | Rent changes, Buy doesn't (e2e); ≥ 15 fps scrub. **→ merge app to main** | 30–36 |
| **A7** | M7 | Demo mode (`?demo=1`) + presentation mode (`?present=1`); About/Formulas/Validation views; accessibility; deploy to GitHub Pages | Spec §6.6–6.7, §8; req §8, §11 | Full demo offline; public URL < 3 s. **→ merge app to main at M7** | 36–41 |

### Humans

| When | Task |
|---|---|
| H0 (hour ~2) | Answer M0 questions in `answers.md`; check the stub on main |
| Every sync (PLAN of build-plan.md §2) | Read both logs' `## Open questions`, answer in `answers.md`, push |
| M3/M4/M6/M7 | Check the gate, tag `main` |
| Throughout | Presentation track (captures, video, deck, project page), novice test (M7) |

## 5. Handoff checklist (Pipeline → App)

- [ ] Tests and sanity green on `pipeline`.
- [ ] `CONTRACT.md` version + changes; `manifest.json` `contract_version` matches.
- [ ] Data size noted (MB); within budget.
- [ ] `## Contract/handoffs` entry: what's new, file list, known issues, SHA.
- [ ] Merged to `main` and pushed.

## 6. Communication summary

| Need | Where |
|---|---|
| "What did I do / what's next?" after compaction | Your log → `## Resume here` |
| Ask the humans | Chat/question tool **and** your log → `## Open questions` |
| Humans answer | `docs/agents/answers.md` (+ chat) |
| Ask the other agent | Your log → `## Requests to <other>` |
| Answer the other agent | Your log → `## Replies to <other>` |
| Data contract | `docs/agents/CONTRACT.md` (Pipeline) |
| Milestone status | Both logs' `## Milestones` table |
