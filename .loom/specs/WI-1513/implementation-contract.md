# WI-1513 Implementation Contract

- Suite path: minimal

## Contract Surface

- `gate_freeze_payload` includes `failure_classifier` using schema `loom-failure-classifier/v1`.
- `failure_classifier.supported_classifiers` includes the #1513 stable classifier vocabulary.
- `failure_classifier.findings[]` includes `classifier`, `failure_kind`, `input`, `result`, `severity`, `evidence_locator`, `next_action`, and `messages`.
- Existing gate freeze pass/block/fallback behavior is preserved.

## Consumer Boundary

- #1512 may consume the stable classifier vocabulary in hosted admission.
- #1533/#1534 may consume the classifier names for closeout gate/docs.
- #1514 may document the generic gate freeze classifier names after this PR lands.

## Non-Goals

- Do not implement hosted admission, closeout-specific gate behavior, PR metadata rendering, Work Item startup audit, one-shot closeout run, or final release/no-release closeout.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
- targeted `failure_classifier_payload` import check
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1513 --json`
- `git diff --check`
