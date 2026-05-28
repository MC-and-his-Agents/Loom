# WI-1134 Plan

- Suite path: minimal

## Implementation Plan

- Add a shared suite gate validation helper that runs `suite evidence validate` and `suite carrier validate` read-only.
- Add `suite_gate_validation` payloads and `suite-evidence-validate` / `suite-carrier-validate` steps to pre-review, implementation review flow, and merge-ready flow.
- Make implementation `review record --decision allow` consume suite evidence/carrier validators and fail closed on blocking or fallback results.
- Store suite validation commands and consumed evidence-map / task-carrier locators in implementation review `consumed_inputs`.
- Keep the authority boundary explicit: suite validation is gate input evidence only.
- Extend CLI contract checks for pre-review, review, and merge-ready suite gate consumption.
- Update gate-chain and full spec suite CLI surface docs.

## Scenario Mapping

- Scenario S1 -> structural validation evidence: `tools/check_cli_contract.py` asserts pre-review suite gate steps and payload.
- Scenario S2 -> structural validation evidence: `tools/check_cli_contract.py` asserts implementation review flow suite gate payload; review record behavior is validated by focused `review record` command before final review.
- Scenario S3 -> structural validation evidence: `tools/check_cli_contract.py` asserts merge-ready suite gate steps and payload; suite validator fixtures continue to cover stale evidence and carrier truth conflict blocking behavior.

## Acceptance Mapping

- A1 -> test evidence: active pre-review payload assertion in `tools/check_cli_contract.py`.
- A2 -> test evidence: active review gate payload assertion in `tools/check_cli_contract.py`.
- A3 -> behavior evidence: `handle_review(record)` suite gate block path in `loom_flow.py`.
- A4 -> behavior evidence: `review_payload["consumed_inputs"]` suite validation locator fields in `loom_flow.py`.
- A5 -> test evidence: active merge-ready payload assertion in `tools/check_cli_contract.py` plus existing suite evidence/carrier negative fixtures.
- A6 -> behavior evidence: `suite_gate_validation.authority_boundary.does_not_replace`.
- A7 -> structural check evidence: focused `rg` for `/speckit`, `.specify`, `suite_gate_validation`, and closeout scope.

## Validation Commands

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `python3 tools/loom.py suite validate --target . --item WI-1134 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1134 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1134 --json`
- `git diff --check`
- focused `rg`
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
