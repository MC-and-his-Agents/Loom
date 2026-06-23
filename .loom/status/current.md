# Current Status

## Derived Fact Chain View

- Item ID: WI-1739
- Goal: 将 metadata repair、carrier refresh 与 shadow parity 纳入 ship 前置修复链
- Scope: Issue #1739: make `loom ship --apply` run safe metadata repair, carrier refresh, and shadow parity before PR metadata preflight, PR gate, and controlled merge check.
- Execution Path: issue #1739 -> branch work/1739-ship-repair-chain -> PR pending -> controlled merge -> closeout
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1739.md
- Review Entry: .loom/reviews/WI-1739.json
- Validation Entry: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group closeout-wrapper
- Closing Condition: PR merged and issue #1739 closed with ship repair-chain evidence.
- Current Checkpoint: merge
- Current Stop: WI-1739 implementation, spec review, implementation review, PR metadata preflight, carrier refresh, and shadow parity are ready for PR gate and hosted checks.
- Next Step: Run PR gate, wait for hosted checks on PR #1768, then perform controlled merge and closeout sync.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 targeted validation passed for WI-1739: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group closeout-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1739 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1739 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1739 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py carrier refresh --target . --item WI-1739 --apply; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py pr-metadata preflight --target . --surface merge_ready --item WI-1739 --issue 1739 --pr 1768 --branch work/1739-ship-repair-chain --head-sha 4b187fe64fe857abed4f529023fa555349247b41.
- Recovery Boundary: WI-1739 owns loom ship --apply pre-merge repair-chain sequencing and focused contract coverage only; it does not implement closeout e2e regression, validation profile selection, or release behavior.
- Current Lane: ship-repair-chain

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1739 ship repair-chain lane started in issue-scoped worktree `work/1739-ship-repair-chain`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1739.md`.
- Diagnostics Entry: `loom ship --apply` now runs safe metadata repair, carrier refresh apply, and blocking shadow parity before PR metadata preflight and merge gates.
- Verification Entry: Targeted ship wrapper, pr-metadata, closeout wrapper, py_compile, carrier refresh, and shadow parity checks are consumed before PR.
- Lane Entry: ship-repair-chain

## Sources

- Static Truth: .loom/work-items/WI-1739.md
- Dynamic Truth: .loom/progress/WI-1739.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
