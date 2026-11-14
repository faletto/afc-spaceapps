# Data contract (pipeline → app)

*Single writer: **Pipeline Claude**. App Claude checks this and `app/public/data/manifest.json` → `contract_version` at every session start.*

## Current version: **v0** (draft; becomes v1 at H0)

Definition: `docs/technical-spec.md` §5 (files, columnar schema, tile layout) + `config.json` keys (spec §4) + golden-vector schema (`pipeline/tests/golden/`, from v2).

## Change log
| Version | Date | Handoff | Change | Files regenerated | Breaking? |
|---|---|---|---|---|---|
| v0 | 14 Nov | — | Spec §5 as written | — | — |

## Rules
- Every breaking change bumps the version **in the same commit** as the updated `stub.py` output, golden vectors and the `manifest.json` field.
- Additive changes (new optional column, new file) bump the minor note but not the version; App may ignore them.
- App requests changes via `## Requests to Pipeline Claude` in `app-log.md`.
