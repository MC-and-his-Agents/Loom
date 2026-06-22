# Current Status

## Derived Fact Chain View

- Item ID: WI-1717
- Goal: 补齐 CLI/plugin freshness 最小回归覆盖。
- Scope: tools/check_cli_contract.py freshness fixtures and WI-1717 carriers only; no release closeout. Ownership constraints: main executor owns `tools/check_cli_contract.py`, WI-1717 `.loom/**` carriers, and `.loom/progress/WI-1717-build-evidence.json`; no release files, legacy installer behavior, payload hash algorithm changes, host mutation semantics, or broad fixture framework are in scope.
- Execution Path: issue #1717 -> branch work/1717-freshness-fixtures -> worktree /Users/mc/dev/Loom-WI-1717-freshness-fixtures -> targeted tests -> PR -> closeout.
- Workspace Entry: /Users/mc/dev/Loom-WI-1717-freshness-fixtures
- Recovery Entry: .loom/progress/WI-1717.md
- Review Entry: .loom/reviews/WI-1717.json
- Validation Entry: python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 test/plugin_payload_hash_test.py; git diff --check
- Closing Condition: PR for work/1717-freshness-fixtures is merged, issue #1717 is closed, and closeout consumes PR, issue, target branch, and repo carrier readback.
- Current Checkpoint: build
- Current Stop: Freshness fixture assertions, suite carriers, validation evidence, and build evidence are integrated for WI-1717.
- Next Step: Record review, open PR, and merge after hosted checks pass.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 local checks passed: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 test/plugin_payload_hash_test.py`; `git diff --check`; `python3 tools/loom.py suite validate --target . --item WI-1717 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1717 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1717 --json`; `python3 tools/loom.py fact-chain --target . --item WI-1717 --json`; `python3 tools/loom.py build --target . --item WI-1717 --build-evidence .loom/progress/WI-1717-build-evidence.json --json`.
- Recovery Boundary: WI-1717 owns `tools/check_cli_contract.py` freshness fixture assertions and WI-1717 carriers only. It does not publish v0.19.0 or change release closeout behavior.
- Current Lane: freshness-fixtures

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1717 build started in issue-scoped worktree `work/1717-freshness-fixtures`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1717.md`.
- Diagnostics Entry: `loom version` and `loom version --json` expose freshness action, surface compatibility, and plugin refresh guidance.
- Verification Entry: Targeted CLI contract, payload hash tests, diff checks, suite validation, fact-chain, and build evidence consumption passed before PR.
- Lane Entry: freshness-fixtures

## Sources

- Static Truth: .loom/work-items/WI-1717.md
- Dynamic Truth: .loom/progress/WI-1717.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
