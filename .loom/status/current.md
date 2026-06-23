# Current Status

## Derived Fact Chain View

- Item ID: WI-1742
- Goal: 补齐 inline / host-only closeout 端到端回归，让普通 light/standard ship apply 不默认创建 closeout PR。
- Scope: tools/check_cli_contract.py ship-wrapper fixture；WI-1742 Loom carriers and suite evidence only。Ownership constraints are limited to `tools/check_cli_contract.py`, `.loom/work-items/WI-1742.md`, `.loom/progress/WI-1742.md`, `.loom/progress/WI-1742-build-evidence.json`, `.loom/specs/WI-1742/**`, `.loom/status/current.md`, `.loom/bootstrap/init-result.json`, and WI-1742 shadow evidence.
- Execution Path: issue-scoped worktree /Users/mc/dev/Loom-WI-1742-closeout-e2e on branch work/1742-closeout-e2e
- Workspace Entry: /Users/mc/dev/Loom-WI-1742-closeout-e2e
- Recovery Entry: .loom/progress/WI-1742.md
- Review Entry: .loom/reviews/WI-1742.json
- Validation Entry: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper
- Closing Condition: PR merged, issue #1742 closed, carrier refresh and shadow parity pass; ownership constraints remain limited to WI-1742 regression coverage and carriers.
- Current Checkpoint: merge
- Current Stop: WI-1742 implementation, build evidence, spec review, and implementation review are recorded; PR creation and merge gates are next.
- Next Step: Push branch, create PR for issue #1742, update PR metadata, then run PR gate and controlled merge.
- Blockers: None
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
