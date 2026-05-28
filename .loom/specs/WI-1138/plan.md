# WI-1138 Plan

- Suite path: minimal

## Implementation Plan

- Add `--item` to delivery command parsing so `loom verify --item <item>` can express a Work Item gate requirement.
- Add installed-state/profile requirement parsing for `suite_validation` and optional `suite_item`.
- Keep `doctor` as the first verify input and only run suite validation after doctor passes.
- Run read-only `suite_validate_payload` when suite validation is required.
- Extend CLI contract fixtures for optional pass, declared-support optional pass, profile-required pass, and Work Item-required block.
- Document verify/profile requirement boundaries.

## Scenario Mapping

- S1 -> automated: `tools/check_cli_contract.py` valid installed-state verify fixture.
- S2 -> automated: `tools/check_cli_contract.py` declared support verify fixture.
- S3 -> automated: `tools/check_cli_contract.py` profile-required verify fixture.
- S4 -> automated: `tools/check_cli_contract.py` Work Item gate missing suite fixture.

## Acceptance Mapping

- A1 -> test evidence: verify fixture checks `suite_validation_requirement`.
- A2 -> test evidence: valid installed-state verify has `suite_validation: null`.
- A3 -> test evidence: declared support verify remains optional.
- A4 -> test evidence: profile-required fixture passes with minimal suite.
- A5 -> test evidence: missing suite fixture blocks.
- A6 -> structural evidence: verify helper only calls `suite_validate_payload`.
- A7 -> structural check: installed-state and full suite surface docs state CLI evidence boundary.
- A8 -> structural check: focused `rg` for `/speckit` and `.specify`.

## Validation Commands

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `python3 tools/loom.py suite validate --target . --item WI-1138 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1138 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1138 --json`
- `git diff --check`
- focused `rg` for `suite_validation`, `suite validate`, `declared_support`, `/speckit`, and `.specify`
- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- release/version/package checks if touched by the final diff.
