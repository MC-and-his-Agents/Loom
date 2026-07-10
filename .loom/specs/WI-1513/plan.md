# WI-1513 Plan

## Implementation Steps

1. Add the stable #1513 classifier vocabulary and default next actions.
2. Map existing gate freeze input names and failure kinds to normalized classifiers.
3. Replace the raw gate freeze `failure_classifier.findings` dump with normalized `loom-failure-classifier/v1` findings.
4. Extend focused CLI contract coverage for supported vocabulary, next actions, and PR metadata drift classification.
5. Sync generated/runtime skill copies for the shared runtime script.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
- targeted `failure_classifier_payload` import check
- PR #1564 metadata preflight/readback
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1513 --json`
- `git diff --check`

## Test Strategy

- Acceptance test mapping:
  - A1 -> test evidence: aggregate CLI contract checks schema/version through normalized payload construction.
  - A2 -> test evidence: aggregate CLI contract checks supported classifier vocabulary.
  - A3 -> test evidence: aggregate gate freeze PR body drift fixture checks `pr_metadata_drift`.
  - A4 -> test evidence: targeted classifier import check maps all listed classes and verifies next actions.
  - A5 -> test evidence: aggregate CLI contract preserves existing gate freeze and PR gate pass/block semantics.


## Dependencies

- Consumes #1508/#1510/#1511/#1554 as stable gate freeze, shadow/carrier, review binding, and wrapper surfaces.
- Provides stable classifier names for #1512, #1533, #1514, and #1534.
- Does not block #1541/#1542 exploration, but downstream consumers must not invent duplicate classifier schema.

## Scope Guard

- Do not edit hosted workflow semantics.
- Do not edit closeout gate behavior.
- Do not edit PR metadata render/update behavior.
- Do not perform host issue/PR mutation except PR #1564 creation/readback.
