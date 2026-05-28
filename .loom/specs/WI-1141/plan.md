# WI-1141 Plan

- Suite path: minimal

## Implementation Plan

- Add shared helpers that normalize suite validation and suite gate consumed locators into review record `consumed_inputs`.
- Preserve consistency-analysis locator fields even when the current CLI surface reports `null` or no current locator.
- Keep review decision authority in the single `review_entry`; consumed suite CLI data remains evidence-only.
- Extend CLI contract checks to assert spec review and implementation review record consumption payloads.
- Sync generated `skills/` runtime and `.loom/bin/loom_flow.py`.
- Refresh Loom carriers and validation evidence for #1141.

## Scenario Mapping

- S1 -> automated: `tools/check_cli_contract.py` records a spec review and asserts suite validation locators in `consumed_inputs`.
- S2 -> automated: `tools/check_cli_contract.py` records an implementation review and asserts suite evidence/carrier locator fields in `consumed_inputs`.
- S3 -> structural: review payload continues to use one `review_entry`, and authority boundary remains review record decision rather than CLI output.

## Acceptance Mapping

- A1 -> test evidence: spec review consumed-input assertions in `tools/check_cli_contract.py`.
- A2 -> test evidence: implementation review consumed-input assertions in `tools/check_cli_contract.py`.
- A3 -> structural evidence: review record schema still stores `decision` / `kind` as authority and CLI locator fields under `consumed_inputs`.
- A4 -> automated evidence: `python3 tools/check_cli_contract.py`.
- A5 -> structural evidence: `python3 tools/skills_surface.py check` and runtime copy hash checks.

## Validation Commands

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1141 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1141 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1141 --json`
- `git diff --check`
- focused `rg` for `suite_consistency_analysis`, `suite_validation`, `suite_evidence_validation`, `/speckit`, and `.specify`
- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- release/version/package checks if touched by final diff.
