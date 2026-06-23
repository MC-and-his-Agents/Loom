# WI-1717 Plan

## Suite Contract

- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1717/spec.md
- Produces: targeted regression assertions in `tools/check_cli_contract.py`.

## Implementation Goal

Extend the existing adoption-host-metadata contract check instead of adding a new fixture harness.

## Phase 1

- Objective: cover the missing freshness variants.
- Deliverable: add assertions for compatible/current surface, incompatible runtime surface, and short `loom version` action output.
- Exit condition: `python3 tools/check_cli_contract.py --surface adoption-host-metadata` passes.

## Phase 2

- Objective: preserve hash regression coverage.
- Deliverable: keep `test/plugin_payload_hash_test.py` passing.
- Exit condition: targeted hash test and `git diff --check` pass.

## Validation

- `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- `python3 test/plugin_payload_hash_test.py`
- `git diff --check`
- `python3 tools/loom.py suite validate --target . --item WI-1717 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1717 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1717 --json`
- Scenario validation mapping:
  - S1 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S2 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S3 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`

## Test Strategy

- Regression coverage: extend the existing `adoption-host-metadata` surface and keep the existing plugin payload hash test.
- Acceptance validation mapping:
  - A1 -> test evidence: CLI/latest and already-current assertions in `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - A2 -> test evidence: stale and metadata-missing payload assertions in `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - A3 -> test evidence: runtime plugin surface incompatibility assertion in `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - A4 -> test evidence: short `loom version` action output assertion in `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - A5 -> test evidence: `python3 test/plugin_payload_hash_test.py`

## Dependencies

- Blocking inputs: #1715 and #1716 implementation surfaces, already closed.
- Required coordination: #1718 consumes this as release readiness evidence.
- Rollback boundary: revert the `tools/check_cli_contract.py` assertions and WI-1717 carriers together.
