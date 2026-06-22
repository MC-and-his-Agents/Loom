# Current Status

## Derived Fact Chain View

- Item ID: WI-1717
- Goal: 补齐 CLI/plugin freshness 最小回归覆盖。
- Scope: tools/check_cli_contract.py freshness fixtures and WI-1717 carriers only; no release closeout. Ownership constraints: main executor owns `tools/check_cli_contract.py`, WI-1717 `.loom/**` carriers, and `.loom/progress/WI-1717-build-evidence.json`; no release files, legacy installer behavior, payload hash algorithm changes, host mutation semantics, or broad fixture framework are in scope.
- Execution Path: issue #1717 -> branch work/1717-freshness-fixtures -> worktree `.loom/..` -> targeted tests -> PR -> closeout. Local workspace path is recorded in the issue workspace comment.
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1717.md
- Review Entry: .loom/reviews/WI-1717.json
- Validation Entry: python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 test/plugin_payload_hash_test.py; git diff --check
- Closing Condition: PR for work/1717-freshness-fixtures is merged, issue #1717 is closed, and closeout consumes PR, issue, target branch, and repo carrier readback.
- Current Checkpoint: closed_out
- Current Stop: WI-1717 closed out by closeout run: PR #1755 merged at bad2de924c562b3cb4e1392b5a7a398edba2544d, issue #1717 closed, host reconciliation consumed, terminal carrier metadata written, status/shadow refresh completed, and final closeout check passed.
- Next Step: No further WI-1717 implementation work remains.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 local checks passed: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 test/plugin_payload_hash_test.py`; `git diff --check`; `python3 tools/loom.py suite validate --target . --item WI-1717 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1717 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1717 --json`; `python3 tools/loom.py fact-chain --target . --item WI-1717 --json`; `python3 tools/loom.py build --target . --item WI-1717 --build-evidence .loom/progress/WI-1717-build-evidence.json --json`; `python3 tools/loom_flow.py runtime-parity validate --target .`.
- Recovery Boundary: WI-1717 owns `tools/check_cli_contract.py` freshness fixture assertions and WI-1717 carriers only. It does not publish v0.19.0 or change release closeout behavior.
- Current Lane: post-merge-closeout-run

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
