# WI-1554 Implementation Contract

- Suite path: minimal

## Contract Surface

- `tools/loom.py merge check|run` exposes `{check,run} pr-number` in help output.
- The wrapper rejects the literal placeholder `pr` before runtime delegation.
- Runtime delegation receives `--pr <number>` and never receives the literal placeholder as an argument value.
- `--work-item`, `--head-sha`, and `--merge-method` remain preserved.
- `tools/loom.py closeout` forwards runtime-supported `closeout check` parameters including `--item`, host object ids, branch, owner/repo, gate profile, fixture payload files, required-check readback files, and `--skip-gate`.
- `tools/loom.py gate closeout` remains a read-only facade over runtime `closeout check` and preserves provided closeout arguments.
- `tools/check_cli_contract.py --surface merge-wrapper` covers the regression without requiring a live PR or host write.
- `tools/check_cli_contract.py --surface governance-closeout` covers closeout and gate closeout wrapper/runtime parameter preservation without requiring host writes.

## Consumer Boundary

- Review, PR gates, hosted checks, merge operators, and milestone/12 closeout may consume this contract as the #1554 wrapper/runtime parameter matrix for merge and closeout command surfaces.
- #1514/#1534/#1515 must readback PR #1562 and #1554 closeout evidence before consuming #1554 as complete.

## Non-Goals

- Do not implement retained Work Item parsing or closeout item lookup.
- Do not implement #1555 one-shot post-merge closeout run.
- Do not change hosted admission, classifier taxonomy, closeout freeze profile semantics, release behavior, closeout gate semantics, or external host writes.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge check pr`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py closeout --target . --item WI-1554 --issue 1554 --branch work/1554-wrapper-closeout-contract --gate-profile closeout-contract --skip-gate --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate closeout --target . --item WI-1554 --issue 1554 --branch work/1554-wrapper-closeout-contract --gate-profile closeout-contract --skip-gate --json`
- `git diff --check`
