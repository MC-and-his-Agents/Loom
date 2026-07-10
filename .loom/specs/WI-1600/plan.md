# WI-1600 Plan

## Implementation Steps

1. Remove issue prose as an active dependency source.
2. Keep GitHub native dependency and structured machine block parsing.
3. Update provenance vocabulary, fixtures, and docs/skill references.
4. Regenerate runtime copies and demo bootstrap fixtures.

## Validation

- `python3 tools/loom.py workspace audit --target . --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `python3 tools/skills_surface.py check`
- `make loom-demo-new-project-check`
- `git diff --check`
- PR #1604 metadata readback/preflight against the current head

## Test Strategy

- Acceptance test mapping:
  - A1 -> test evidence: prose-only dependency fixture produces no active dependency.
  - A2 -> test evidence: GitHub native dependency fixture remains active.
  - A3 -> test evidence: structured machine block fixture remains active.
  - A4 -> test evidence: provenance/docs fixture distinguishes prose note from dependency truth.

## Scope Guard

- Do not change closeout PR role model.
- Do not change docs/skills convergence owned by #1598.
- Do not change release resume or publishing behavior.
- Do not change host API auth behavior.
