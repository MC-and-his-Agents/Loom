# WI-1122 Plan

## Implementation Plan

1. Reuse the existing `suite inspect` and `suite validate` helper structure.
2. Add repo-local parsing for not_applicable and deferred records in suite artifacts.
3. Require not_applicable records to carry artifact binding, rationale, consumer boundary, and recheck condition.
4. Block minimal path readiness when full-path artifacts lack valid not_applicable coverage.
5. Block deferred records when they are the only explanation for a not_applicable readiness gap.
6. Extend CLI contract fixtures for valid minimal, invalid not_applicable, deferred-only, and suite-level not_applicable cases.
7. Update CLI surface docs to mark #1122 as the not_applicable rationale slice.

## Validation Plan

- `python3 tools/check_cli_contract.py`
- `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `git diff --check`
- focused `rg` for `not_applicable`, `deferred_as_completed`, `invalid_not_applicable_rationale`, `/speckit`, and `.specify`
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1122`

## Out Of Scope

- No #1123 spec/plan mapping checks.
- No #1124 final failure taxonomy expansion.
- No #1125 `flow spec-review` integration.
