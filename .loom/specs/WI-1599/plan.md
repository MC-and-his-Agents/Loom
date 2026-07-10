# WI-1599 Plan

## Implementation Steps

1. Add explicit closeout PR role vocabulary and CLI input handling.
2. Surface current role and role set in closeout check/run output.
3. Update fixtures and generated runtime copies.
4. Keep release publishing and dependency parser semantics out of scope.

## Validation

- `python3 tools/loom.py workspace audit --target . --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `python3 tools/skills_surface.py check`
- `make loom-demo-new-project-check`
- `git diff --check`
- PR #1605 metadata readback/preflight against the current head

## Test Strategy

- Acceptance test mapping:
  - A1 -> test evidence: closeout check/run contract fixture for explicit PR role input.
  - A2 -> test evidence: role vocabulary fixture covering implementation, release, carrier sync, and final closeout roles.
  - A3 -> test evidence: role-only closeout fixture without legacy generic PR requirement.
  - A4 -> test evidence: invalid/missing role diagnostics fixtures.

## Scope Guard

- Do not change release publishing logic.
- Do not change issue prose dependency parser semantics.
- Do not change host API auth behavior.
- Do not change PR metadata dry-run/update semantics.
