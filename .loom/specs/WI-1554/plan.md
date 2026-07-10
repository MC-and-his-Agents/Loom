# WI-1554 Plan

## Implementation Steps

1. Change the `tools/loom.py merge` positional PR argument to `pr-number` and parse it as an integer.
2. Convert the parsed PR number back to string when passing `--pr` to the controlled merge runtime.
3. Add a focused `merge-wrapper` CLI contract surface that imports `tools/loom.py`, stubs runtime delegation, and proves numeric PR forwarding plus placeholder rejection.
4. Forward runtime-supported `closeout check` parameters from `loom closeout`, including retained Work Item, host object, branch, gate profile, payload fixture, and readback options.
5. Add focused `closeout` and `gate closeout` wrapper argument preservation checks to the `governance-closeout` CLI contract surface.
6. Include the wrapper checks in aggregate CLI contract coverage without implementing #1555 one-shot closeout run behavior.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1554 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1554 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1554 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1554 --build-evidence .loom/progress/WI-1554-build-evidence.json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge check pr`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py closeout --target . --item WI-1554 --issue 1554 --branch work/1554-wrapper-closeout-contract --gate-profile closeout-contract --skip-gate --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate closeout --target . --item WI-1554 --issue 1554 --branch work/1554-wrapper-closeout-contract --gate-profile closeout-contract --skip-gate --json`
- `git diff --check`

## Dependencies

- Consumes issue #1554 as the parent wrapper/runtime contract item.
- Consumes #1494 only as the existing runtime `--item` binding; does not implement #1495/#1496 retained lookup behavior.
- Does not block #1510/#1512/#1513/#1541/#1542 implementation lanes.
- Downstream convergence consumers #1514/#1534/#1515 must readback #1554 state and PR #1562 evidence after this slice merges.

## Scope Guard

- Do not edit PR body, issue body, or host state from subagents.
- Do not implement #1555 one-shot post-merge closeout run in this PR.
- Do not change hosted admission, failure classifier, release/no-release closeout, or closeout freeze profile semantics.
