# WI-1742 Implementation Contract

## Ownership

WI-1742 may modify only:

- `tools/check_cli_contract.py`
- `.loom/work-items/WI-1742.md`
- `.loom/progress/WI-1742.md`
- `.loom/progress/WI-1742-build-evidence.json`
- `.loom/specs/WI-1742/**`
- `.loom/reviews/WI-1742.json`
- `.loom/reviews/WI-1742.spec.json`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- WI-1742 shadow evidence for status hash refresh

## Required Behavior

- Add deterministic ship-wrapper fixture coverage for light ordinary host-only closeout.
- Add deterministic ship-wrapper fixture coverage for standard ordinary host-only closeout.
- Assert host reconciliation and closeout check occur after controlled merge and read back issue, PR, merge commit, and target branch facts.
- Assert release and versioned terminal carrier inputs block before merge and point to the explicit closeout queue path.

## Non-Goals

- No real release publish.
- No GitHub Release, tag, or npm publish.
- No GitHub permission model change.
- No changes to #1711-#1722 or v0.19.0 state.

## Validation Contract

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1742 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1742 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1742 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py build --target . --item WI-1742 --build-evidence .loom/progress/WI-1742-build-evidence.json --json`
