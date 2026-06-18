# WI-1555 Plan

- Suite path: not_applicable

## Implementation Steps

- Add the `closeout run` command surface to `tools/loom.py`.
- Delegate dry-run/apply through existing `reconciliation sync`, `closeout check`, `carrier closeout-sync`, `recovery writeback`, and `carrier refresh` runtime primitives.
- Emit a `loom-closeout-run/v1` payload with ordered steps, terminal metadata, evidence locators, failure classifier, and next action.
- Add a narrow `closeout-wrapper` CLI contract surface covering dry-run, apply, and blocked apply behavior.

## Validation

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper`
- `python3 tools/loom.py closeout run --target . --item WI-1582 --issue 1582 --pr 1583 --branch work/1582-closeout-hosted-admission --json`
- PR metadata render/readback/preflight for PR #1585.
