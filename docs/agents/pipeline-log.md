# Pipeline Claude — log

*Single writer: **Pipeline Claude**. Others read only. Keep `## Resume here
- Branch: `pipeline` · Contract: **v1** (stub, H0) · P0 done (see Done log for SHA)
- Env: `make setup` (uv venv py3.11 at repo-root `.venv`), `make stub`, `make test`; stub ≈ 41 MB in `app/public/data/` (committed once; avoid regenerating/committing churn)
- Next: P1 — Horizons fetch + parser + `ephemeris.py`, `geometry.py`; terrain (global + polar) in a worktree subagent. Read spec §3.1–3.4.
- Blockers: none. Note: system python is 3.15; always use `.venv` (3.11).

## Milestones
| WP | Status | Branch SHA | Merged to main | Notes |
|---|---|---|---|---|
| P0 | ✅ | see Done log | H0 | stub + contract v1 |
| P1 | ⬜ | | | |
| P2 | ⬜ | | | |
| P3 | ⬜ | | | |
| P4 | ⬜ | | | |
| P5 | ⬜ | | | |
| P6 | ⬜ | | | |

## Contract/handoffs
- H0 · 14 Nov · contract v1 · stub data (fake values, real formats), ≈41 MB, 738 files. Details in CONTRACT.md 'v1 concrete details'. Known: polar ≈78k plots (disk to 85°S), not 91k; polar projection is a stand-in.
<!-- newest first: H#, date/time, contract vN, main@sha, what's new, files, size MB, known issues -->

## Open questions
- Q-P1 · 14 Nov · Stub data (41 MB) committed to git; real data likely larger (detail JSON). Default: ASSUMED commit if < 50 MB total, else Release asset (per answers.md).
<!-- Q-P#: date · question · context · my default (ASSUMED if proceeding) -->

## Answered
<!-- Q-P#: answer · source (answers.md / chat) · date -->

## Requests to App Claude
<!-- R-P#: what I need from App · why · by when -->

## Replies to App Claude
<!-- reply to R-A#: … -->

## Done log
<!-- newest first: date time · WP · what · sha · tests -->
