# WI-1554 Implementation Contract

- Suite path: minimal

## Contract Surface

- `tools/loom.py merge check|run` exposes `{check,run} pr-number` in help output.
- The wrapper rejects the literal placeholder `pr` before runtime delegation.
- Runtime delegation receives `--pr <number>` and never receives the literal placeholder as an argument value.
- `--work-item`, `--head-sha`, and `--merge-method` remain preserved.
- `tools/check_cli_contract.py --surface merge-wrapper` covers the regression without requiring a live PR or host write.

## Consumer Boundary

- Review, PR gates, hosted checks, merge operators, and milestone/12 closeout may consume this contract only as the merge wrapper PR argument fix.
- #1554 remains open for the broader wrapper/runtime contract matrix after this PR merges.

## Non-Goals

- Do not implement retained Work Item parsing or closeout item lookup.
- Do not change `closeout`, `gate closeout`, hosted admission, classifier taxonomy, closeout freeze profile semantics, release behavior, or external host writes.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge check pr`
- `git diff --check`
