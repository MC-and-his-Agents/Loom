# WI-1131 Plan

- Suite path: minimal

## Implementation Plan

- Add `suite carrier inspect` and `suite carrier validate` to the implemented CLI help matrix.
- Parse repo-local `.loom/specs/<item>/task-carrier.md` tables into normalized carrier rows.
- Report recognized carrier types, normalized statuses, relationships, Work Item truth locators, and the truth boundary that carrier state remains tracking-only.
- Validate required carrier fields, supported type/status/relationship values, Work Item backlinks, repo-local carrier locator readability, primary carrier uniqueness, deferred-as-completed, and carrier truth conflicts.
- Extend `tools/check_cli_contract.py` with pass and fail-closed fixtures for carrier inspect/validate.
- Update CLI surface docs to record #1131 behavior.

## Scenario Mapping

- Scenario S1 -> structural validation evidence: `python3 tools/check_cli_contract.py` carrier inspect pass fixture.
- Scenario S2 -> structural validation evidence: `python3 tools/check_cli_contract.py` missing locator and invalid field fixtures.
- Scenario S3 -> structural validation evidence: `python3 tools/check_cli_contract.py` truth conflict and deferred-as-completed fixtures.

## Acceptance Mapping

- A1 -> test evidence: `python3 tools/check_cli_contract.py` carrier inspect envelope assertions.
- A2 -> test evidence: carrier inspect vocabulary, locator, row, and consumed contract assertions.
- A3 -> test evidence: missing task-carrier fixture.
- A4 -> test evidence: carrier validate invalid type/status/relationship checks.
- A5 -> test evidence: Work Item backlink and primary uniqueness validation logic plus focused `rg`.
- A6 -> test evidence: carrier truth conflict and deferred-as-completed fixtures.
- A7 -> structural check evidence: focused `rg` for `suite carrier`, `carrier_truth_conflict`, `/speckit`, and `.specify`.

## Validation Commands

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py`
- `python3 tools/loom.py suite validate --target . --item WI-1131 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1131 --json`
- `python3 tools/loom.py suite carrier inspect --target . --item WI-1131 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1131 --json`
- `git diff --check`
- focused `rg`
- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
