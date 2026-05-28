# WI-1130 Plan

- Suite path: minimal

## Implementation Plan

- Extend `tools/loom.py` evidence-map validation with a current freshness context.
- Keep evidence-map bindings opt-in: only explicit `head_sha`, `reviewed_head`, `pr_head`, or validation summary digest fields are compared.
- Treat repo-local source locators for `present` evidence as required readable inputs.
- Extend `tools/check_cli_contract.py` with fixtures for source locator missing, head drift, PR head drift, validation summary drift, and existing stale behavior.
- Update CLI surface docs to record the new fail-closed evidence freshness checks.

## Scenario Mapping

- Scenario S1 -> structural validation evidence: `python3 tools/check_cli_contract.py` missing source locator fixture.
- Scenario S2 -> structural validation evidence: `python3 tools/check_cli_contract.py` head drift and PR head drift fixtures.
- Scenario S3 -> structural validation evidence: `python3 tools/check_cli_contract.py` validation summary digest drift fixture.

## Acceptance Mapping

- A1 -> test evidence: `python3 tools/check_cli_contract.py` evidence validate envelope assertions.
- A2 -> test evidence: missing source locator fixture.
- A3 -> test evidence: head drift and PR head drift fixtures.
- A4 -> test evidence: validation summary digest drift fixture.
- A5 -> test evidence: stale evidence and missing fresh verification fixtures.
- A6 -> structural check evidence: focused `rg` for `suite evidence validate`, `head_or_pr_drift`, `/speckit`, and `.specify`.

## Validation Commands

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py`
- `git diff --check`
- focused `rg`
- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
