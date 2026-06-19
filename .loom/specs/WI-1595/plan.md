# WI-1595 Plan

## Implementation Steps

1. Change PR metadata update so host mutation requires explicit `--apply`.
2. Add focused preflight diagnostics for enum, surface, branch, and head drift.
3. Keep existing PR body prose while replacing only metadata carrier fields.
4. Regenerate skills runtime copies and synchronize demo bootstrap fixtures.

## Validation

- `python3 tools/loom.py workspace audit --target . --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `python3 tools/skills_surface.py check`
- `make loom-demo-new-project-check`
- `git diff --check`
- PR #1603 metadata update/readback/preflight against the current head

## Test Strategy

- Acceptance test mapping:
  - A1 -> test evidence: focused `tools/check_cli_contract.py --surface pr-metadata` dry-run/apply fixture.
  - A2 -> test evidence: focused `tools/check_cli_contract.py --surface pr-metadata` diagnostic fixture.
  - A3 -> test evidence: PR #1603 metadata readback/preflight evidence.

## Scope Guard

- Do not modify host API auth behavior.
- Do not modify closeout PR role model.
- Do not modify release resume or publishing behavior.
- Do not modify issue dependency parser semantics.
