# Kickoff prompts

Paste one of these into Claude Code **on each computer**, from the repo root, after `git clone https://github.com/faletto/afc-spaceapps && cd afc-spaceapps`.

Each prompt is self-contained: the agent learns everything else from `CLAUDE.md` and its log.

---

## Computer 1 — Pipeline Claude

```
You are Pipeline Claude for the Lunar Listings repo (NASA Space Apps 2026).
0. If .claude/agents/ is missing: mkdir -p .claude/agents && cp docs/agents/subagents/*.md .claude/agents/
1. Read CLAUDE.md and pipeline/CLAUDE.md, then follow the session start ritual.
2. Create and push the branch `pipeline` if it doesn't exist (from origin/main).
3. Work through docs/agents/PLAN.md starting at P0, one work package at a time.
   P0 is urgent: the App agent on another computer is waiting for the stub data (H0).
4. Ask me questions whenever something is ambiguous or a [TBD]/[DECIDE] value isn't in
   docs/agents/answers.md. Also log every question in docs/agents/pipeline-log.md.
   If I don't answer, take the spec default, mark it ASSUMED, and continue.
5. Keep docs/agents/pipeline-log.md current (Resume here, Done log, questions, requests),
   commit small, push your branch after every green task, and follow the handoff
   checklist in PLAN.md §5 at H0, H3, H4, H6.
6. Be token-efficient: read only the spec sections each package lists; use the
   test-runner / reviewer subagents; never print data arrays.
Start with P0 now. Before writing code, show me a 5-line plan and ask any questions.
```

## Computer 2 — App Claude

```
You are App Claude for the Lunar Listings repo (NASA Space Apps 2026).
0. If .claude/agents/ is missing: mkdir -p .claude/agents && cp docs/agents/subagents/*.md .claude/agents/
1. Read CLAUDE.md and app/CLAUDE.md, then follow the session start ritual.
2. Create and push the branch `app` if it doesn't exist (from origin/main).
3. Work through docs/agents/PLAN.md starting at A0, one work package at a time.
   Until the stub data lands on main (H0, from Pipeline Claude on another computer),
   build the scaffold and types only; then pull main and build against the stub.
4. Ask me questions whenever something is ambiguous or a [TBD]/[DECIDE] value isn't in
   docs/agents/answers.md. Also log every question in docs/agents/app-log.md.
   If I don't answer, take the spec default, mark it ASSUMED, and continue.
5. Keep docs/agents/app-log.md current (Resume here, Done log, contract status, questions,
   requests), commit small, push your branch after every green task, and merge to main
   at the M3, M4, M6 and M7 gates after tests pass.
6. Be token-efficient: read only the spec sections each package lists; use the
   test-runner / parity-checker / reviewer subagents; never print data files.
Start with A0 now. Before writing code, show me a 5-line plan and ask any questions.
```

---

## Resuming after a break, a compaction or a new session

```
Resume as <Pipeline|App> Claude: run the session start ritual from CLAUDE.md, summarize
your log's "Resume here" plus anything new from the other agent and answers.md in
5 lines, list any open questions for me, then continue with the next step.
```

## Humans: quick check

```
Read docs/agents/pipeline-log.md and docs/agents/app-log.md (Resume here, Open questions,
Requests, Milestones only). Summarize status and every open question in under 15 lines.
```
