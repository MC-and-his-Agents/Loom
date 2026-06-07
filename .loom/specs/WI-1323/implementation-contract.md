# Implementation Contract

## Ownership

- `tools/check_cli_contract.py`: targeted governance intensity escalation and abuse-protection fixtures, plus small assertion helpers.
- `.loom/work-items/WI-1323.md`, `.loom/progress/WI-1323.md`, `.loom/status/current.md`, `.loom/specs/WI-1323/*`, and `.loom/reviews/WI-1323.json`: WI-1323 carrier, suite, evidence, and review truth.

## Non-Goals

- Do not redesign `tiered-gate-consumption-contract.md`, metadata schema fields, PR metadata carrier structure, or gate enum values.
- Do not lower gate strictness to make positive fixtures pass.
- Do not change `tools/loom.py`, `.loom/bin/loom_flow.py`, generated runtime copies, release mechanics, permissions, external runtime behavior, hosted CI configuration, or #1324 parent/final closeout.
- Do not treat unrelated legacy failures as #1323 scope.

## Required Behavior

- docs-governance light/not_applicable positive fixtures must still require fact-chain, current-head review, PR metadata binding, merge checkpoint, PR gate, no-release judgment, controlled merge, and closeout.
- Runtime/code, fixture, release-impacting docs, deferred release judgment, missing not_applicable rationale, suite/metadata mismatch, PR body readback drift, carrier/head mismatch, PR branch mismatch, and stale review/head binding must block through real gate commands.
- Fixture failures must be blocking results, not advisory warnings or string-only assertions.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1323 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py pr-gate check --target . --item WI-1323 --branch work/1323-tier-escalation-abuse-fixtures --head-sha <PR_HEAD> --pr <PR>`
- `git diff --check`
- no-release evidence and current-head review before hosted checks / controlled merge
