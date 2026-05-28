# WI-1141 Implementation Contract

## Ownership

- Runtime source: `src/skills/shared/scripts/loom_flow.py`
- Generated runtime: `skills/shared/scripts/loom_flow.py`, `skills/*/.loom-runtime/shared/scripts/loom_flow.py`, `.loom/bin/loom_flow.py`, and demo bootstrap runtime.
- Contract tests: `tools/check_cli_contract.py`
- Loom carriers: `.loom/work-items/WI-1141.md`, `.loom/progress/WI-1141.md`, `.loom/specs/WI-1141/*`, `.loom/reviews/WI-1141*`, and related runtime/shadow refresh carriers declared in the Work Item.

## Required Behavior

- Review record writes must keep the single authored `review_entry` as the authority for review decisions.
- Suite validation consumption must be recorded under `consumed_inputs` when spec review records an `allow` decision.
- Suite evidence/carrier consumption must be recorded under `consumed_inputs` when implementation review records an `allow` decision.
- Consistency-analysis locator fields must be present when consumed locator payloads are normalized, even when the current suite surface has no locator.

## Non-Goals

- Do not implement `loom suite consistency analyze`.
- Do not create parallel review records or use CLI JSON as review authority.
- Do not add `/speckit.*` command names or `.specify/` layout.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1141 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1141 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1141 --json`
- `python3 tools/skills_surface.py check`
- `git diff --check`
