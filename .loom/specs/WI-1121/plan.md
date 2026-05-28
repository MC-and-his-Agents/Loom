# WI-1121 Plan

## Implementation Plan

1. Reuse the existing `suite inspect` and `suite validate` helper structure.
2. Add path decision collection that can detect invalid or conflicting path decisions.
3. Add required artifact validation for non-file artifacts.
4. Add full path conditional artifact inventory for `research.md`, `contracts.md`, and `readiness-checklist.md`.
5. Extend CLI contract fixtures for conflict, invalid required artifact, and conditional artifact inventory.
6. Update CLI surface docs to mark #1121 as the path/artifact validation deepening slice.

## Validation Plan

- `python3 tools/check_cli_contract.py`
- `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `git diff --check`
- focused `rg` for `suite_path`, `conditional`, `conflicting_suite_path_decision`, `/speckit`, and `.specify`
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1121`

## Out Of Scope

- No #1122 not_applicable/deferred rationale enforcement.
- No #1123 spec/plan mapping checks.
- No #1124 final failure taxonomy expansion.
- No #1125 `flow spec-review` integration.
