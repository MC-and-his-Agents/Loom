# WI-1125 Plan

Consumes Suite path: minimal.

## Validation

- Scenario validation mapping:
  - S1 -> automated: `python3 tools/loom_check.py --profile source --source-surface contract-only .` installed regression plus focused local `flow spec-review` smoke.
  - S2 -> automated: `python3 tools/loom_check.py --profile source --source-surface contract-only .` installed regression for `review record --kind spec_review --decision allow`.

## Test Strategy

- Acceptance test mapping:
  - A1 -> structural check and runtime smoke: `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py flow spec-review --target . --item WI-1124`.
  - A2 -> structural check: `rg -n "gate spec-review|spec-review" tools/loom.py src/skills/shared/scripts/loom_flow.py`.
  - A3 -> test evidence: `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
  - A4 -> test evidence: `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
