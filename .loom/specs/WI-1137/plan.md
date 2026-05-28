# WI-1137 Plan

- Suite path: minimal

## Implementation Plan

- Add a declared suite support parser that reads top-level and layer-level installed-state support declarations.
- Add a doctor `suite-command-surface` check that compares declared suite commands with the existing `loom help --json` command matrix.
- Keep doctor check-only: no full suite validation commands are executed by doctor.
- Extend CLI contract fixtures for undeclared support pass, declared support pass, and declared support drift fail-closed.
- Document `declared_support.suite_commands` in installed-state v2 and full spec suite doctor boundaries.

## Scenario Mapping

- S1 -> automated: `tools/check_cli_contract.py` undeclared installed-state doctor fixture.
- S2 -> automated: `tools/check_cli_contract.py` declared support fixture.
- S3 -> automated: `tools/check_cli_contract.py` declared drift fixture.

## Acceptance Mapping

- A1 -> test evidence: doctor fixture finds `suite-command-surface`.
- A2 -> test evidence: undeclared fixture passes with `declared_support: false`.
- A3 -> behavior and test evidence: command matrix comparison in `tools/loom.py`; declared fixture passes.
- A4 -> test evidence: drift fixture blocks with schema errors.
- A5 -> structural evidence: doctor helper only reads installed-state and command matrix.
- A6 -> structural check: installed-state docs and doctor check describe diagnostic-only boundary.
- A7 -> structural check: focused `rg` for `/speckit` and `.specify`.

## Validation Commands

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `python3 tools/loom.py doctor --target . --json`
- `python3 tools/loom.py suite validate --target . --item WI-1137 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1137 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1137 --json`
- `git diff --check`
- focused `rg` for `suite-command-surface`, `declared_support`, `/speckit`, and `.specify`
- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- release/version/package checks if touched by the final diff.
