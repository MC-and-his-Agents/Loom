# WI-1140 Plan

- Suite path: minimal

## Implementation Plan

- Update shared scenario runtime so build consumes `suite validate` and `suite carrier validate` JSON before build readiness.
- Make suite validation unavailable paths fail closed instead of using embedded suite readiness fallback.
- Keep pre-review/review/merge-ready suite gate payloads as gate input evidence only.
- Update source skill docs and route matrix to describe CLI JSON consumption boundaries.
- Regenerate `skills/` and sync `.loom/bin/loom_flow.py`.
- Extend CLI contract checks to assert build consumes suite CLI JSON.
- Refresh Loom carriers and validation evidence.

## Scenario Mapping

- S1 -> automated: `tools/check_cli_contract.py` active build fixture asserts `suite_validation` and `suite_carrier_validation`.
- S2 -> automated: `tools/check_cli_contract.py` / `loom gate spec-review` consume `suite validate`.
- S3 -> automated: existing active pre-review, review gate, and merge-ready assertions consume `suite_gate_validation`.
- S4 -> structural check: focused `rg` verifies embedded fallback text is removed and CLI JSON unavailable fails closed.

## Acceptance Mapping

- A1 -> test evidence: `assert_suite_build_consumption` in `tools/check_cli_contract.py`.
- A2 -> structural evidence: `spec_suite_validation_payload` returns `cli-json-unavailable` block instead of runtime presence fallback.
- A3 -> test evidence: suite gate consumption assertions for pre-review, review, and merge-ready.
- A4 -> structural check: `src/skills/route-matrix.md`, scenario SKILL docs, and full suite CLI surface docs.
- A5 -> structural check: `python3 tools/skills_surface.py check` and `.loom/bin/loom_flow.py` sha update.
- A6 -> structural check: suite gate authority boundary remains `gate_input_evidence`.
- A7 -> structural check: focused `rg` for `/speckit` and `.specify`.

## Validation Commands

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `python3 tools/loom.py suite validate --target . --item WI-1140 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1140 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1140 --json`
- `python3 tools/loom.py build --target . --item WI-1140 --json`
- `git diff --check`
- focused `rg` for `suite_validation`, `suite_gate_validation`, `cli-json-unavailable`, `runtime formal suite presence`, `/speckit`, and `.specify`
- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- release/version/package checks if touched by final diff.
