# WI-1578 Plan

## Implementation Steps

1. Change PR metadata effective surface logic so closeout requests emit `closeout`.
2. Keep review/pre-review compatibility for declared merge-ready metadata carriers.
3. Update focused pr-metadata fixture expectations.
4. Regenerate skills runtime copies.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `git diff --check`

## Test Strategy

- Acceptance test mapping:
  - A1 -> test evidence: focused `tools/check_cli_contract.py --surface pr-metadata` render fixture.
  - A2 -> test evidence: focused `tools/check_cli_contract.py --surface pr-metadata` closeout preflight fixture.
  - A3 -> test evidence: focused `tools/check_cli_contract.py --surface pr-metadata` review/pre-review compatibility fixture.

## Scope Guard

- Do not modify #1577 carrier files.
- Do not change PR metadata schema fields.
- Do not modify hosted workflow or controlled merge behavior.
