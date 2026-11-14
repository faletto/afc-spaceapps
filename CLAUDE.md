# CLAUDE.md — Lunar Listings (read first, every session)

Two Claude Code agents build this repo **in parallel on different computers**, coordinating only through this GitHub repo. Humans (the team) answer questions and own decisions.

| Agent | Owns (writes) | Branch | Log (its memory + its outbox) |
|---|---|---|---|
| **Pipeline Claude** | `pipeline/`, `config/`, `app/public/data/` (generated), `docs/agents/pipeline-log.md`, `docs/agents/CONTRACT.md` | `pipeline` | `docs/agents/pipeline-log.md` |
| **App Claude** | `app/` (except `app/public/data/`), `docs/agents/app-log.md` | `app` | `docs/agents/app-log.md` |
| **Humans** | `docs/agents/answers.md`, `docs/agents/PLAN.md`, `docs/*.md` specs | `main` | — |

**Never edit a file you don't own.** To ask for a change in someone else's file, write a request in **your own** log (`## Requests to <other>`). Single-writer files mean the two branches never conflict on them.

## Session start ritual (≤ 5 min, every session, after any compaction)
1. `git fetch origin && git status -sb`. On your branch: `git pull --rebase origin <your-branch>`, then `git merge origin/main` (clean; directories are disjoint).
2. Read, in order: **your log's `## Resume here`** → `docs/agents/answers.md` (new answers?) → **the other agent's log** `## Resume here`, `## Requests to <you>` and `## Contract/handoffs` sections only → `docs/agents/CONTRACT.md` (version).
3. Pick the next work package from `docs/agents/PLAN.md`. Read **only** the spec sections it lists.

## Session end ritual (and before you expect a compaction)
1. Run your tests. Commit small, with clear messages.
2. Update your log: rewrite `## Resume here` (≤ 15 lines: done, in progress, next step, blockers, exact commands); append to `## Done log`; update `## Open questions` and `## Requests`.
3. `git push origin <your-branch>`. At a handoff point (PLAN.md), merge to `main` (rebase first, tests green) and push `main`.
4. Record the commit SHA and contract version you built against.

## Ask questions — often, early, visibly
- **Ask the human** (in chat, or with the question tool) whenever:
  - a requirement is ambiguous;
  - a `[TBD]`/`[DECIDE]` value isn't settled in `docs/agents/answers.md`;
  - a change would touch the frozen data contract;
  - a budget is blown (time, size, performance);
  - a test of the science fails in a way that suggests the spec is wrong;
  - before anything destructive (force-push, deleting data, rewriting history).
- **Also write every question into your log** under `## Open questions` (Q-number, date, context, your default). When answered, move it to `## Answered` with the answer, so the other agent sees it.
- **Human not around?** Take the spec's default, write `ASSUMED:` in the log, keep going, and re-ask at the next sync. Don't block on questions that have a sensible default.
- **Question for the other agent?** Put it in `## Requests to <other>` in your log. The other agent answers in its own log. Humans watch both.

## Token efficiency
- Don't read whole specs. `docs/requirements.md` and `docs/technical-spec.md` are long: use `grep -n` and `Read` with offsets on the sections your package lists.
- Logs are the memory: after compaction, re-read `## Resume here`, not the chat history or the specs.
- **Use subagents** (definitions in `.claude/agents/`; if that folder is missing, run `mkdir -p .claude/agents && cp docs/agents/subagents/*.md .claude/agents/` and commit it) for:
  - test runs (`test-runner`, returns a short failure summary);
  - independent review of a finished package (`reviewer`, fresh context);
  - Python ⇄ TypeScript parity (`parity-checker`);
  - wide file searches (built-in Explore).

  Do small edits yourself; don't spawn agents for them.
- Keep outputs small: `pytest -q --maxfail=1`, `npm test -- --silent`. Redirect long logs to files and `tail` them. **Never print arrays, binaries or data files.** Summarize with a short script instead.
- Use plan mode for big packages (horizons, 3D Tour, rent) before coding.
- One work package per session where possible; commit when tests are green.

## Ground truth
- Requirements: `docs/requirements.md` (v2.2 final). How: `docs/technical-spec.md`. Order: `docs/agents/PLAN.md` (agent-level) and `docs/build-plan.md` (human-level).
- Locked decisions: React + deck.gl; Python 3.11 + NumPy/Numba; Earth contact = ≥ 1° above local terrain (`terrain_margin`); analysis year 2028; BASE $5,000, k 6.9.
