# Current Status

## Derived Fact Chain View

- Item ID: WI-1742
- Goal: 补齐 inline / host-only closeout 端到端回归，让普通 light/standard ship apply 不默认创建 closeout PR。
- Scope: tools/check_cli_contract.py ship-wrapper fixture；WI-1742 Loom carriers and suite evidence only。
- Execution Path: issue-scoped worktree /Users/mc/dev/Loom-WI-1742-closeout-e2e on branch work/1742-closeout-e2e
- Workspace Entry: /Users/mc/dev/Loom-WI-1742-closeout-e2e
- Recovery Entry: .loom/progress/WI-1742.md
- Review Entry: .loom/reviews/WI-1742.json
- Validation Entry: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper
- Closing Condition: PR merged, issue #1742 closed, carrier refresh and shadow parity pass.
- Current Checkpoint: build
- Current Stop: WI-1742 implementation added ship-wrapper e2e coverage for light/standard host-only closeout, release blocker, and versioned terminal blocker.
- Next Step: Commit WI-1742 implementation, write review record, open PR, then run PR metadata and merge gates.
- Blockers: None.
- Latest Validation Summary: 2026-06-23 local validation passed: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1742 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1742 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1742 --json.
- Recovery Boundary: WI-1742 owns ship-wrapper closeout e2e regression coverage and WI-1742 carriers only; it does not publish v0.20.0 or alter #1711-#1722/v0.19.0 state.
- Current Lane: closeout-e2e

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1739 ship repair-chain lane started in issue-scoped worktree `work/1739-ship-repair-chain`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1739.md`.
- Diagnostics Entry: `loom ship --apply` now runs safe metadata repair, carrier refresh apply, and blocking shadow parity before PR metadata preflight and merge gates.
- Verification Entry: Targeted ship wrapper, pr-metadata, closeout wrapper, py_compile, carrier refresh, and shadow parity checks are consumed before PR.
- Lane Entry: ship-repair-chain

## Sources

- Static Truth: .loom/work-items/WI-1742.md
- Dynamic Truth: .loom/progress/WI-1742.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
