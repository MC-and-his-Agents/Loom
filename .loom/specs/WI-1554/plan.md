# WI-1554 Plan

## Implementation Steps

1. Change the `tools/loom.py merge` positional PR argument to `pr-number` and parse it as an integer.
2. Convert the parsed PR number back to string when passing `--pr` to the controlled merge runtime.
3. Add a focused `merge-wrapper` CLI contract surface that imports `tools/loom.py`, stubs runtime delegation, and proves numeric PR forwarding plus placeholder rejection.
4. Include the new surface in the aggregate CLI contract suite without broadening this PR into closeout wrapper work.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge check pr`
- `git diff --check`

## Dependencies

- Consumes issue #1554 as the parent wrapper/runtime contract item.
- Does not consume #1494/#1495/#1496 retained Work Item parsing.
- Does not block #1510/#1512/#1513/#1541/#1542 implementation lanes.
- Downstream convergence consumers #1514/#1534/#1515 must still readback final #1554 state after the remaining wrapper/runtime contract surfaces are complete.

## Scope Guard

- Do not edit PR body, issue body, or host state from subagents.
- Do not implement `closeout --item`, `closeout`, `gate closeout`, or #1555 one-shot post-merge closeout run in this PR.
- Do not change hosted admission, failure classifier, release/no-release closeout, or closeout freeze profile semantics.
