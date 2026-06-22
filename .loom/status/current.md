# Current Status

## Derived Fact Chain View

- Item ID: WI-1735
- Goal: 冻结 loom ship 主路径合同与短诊断输出。
- Scope: Issue #1735 only: document dry-run/apply order, auto-repair boundary, blocker classification, short diagnostics, --full-output boundary, closeout policy escalation, and targeted ship-wrapper contract checks. Non-goals: no full repair chain, no merge permission change, no closeout permission change.
- Execution Path: issue #1735 -> branch work/1735-ship-contract -> PR #1744 -> controlled merge -> closeout
- Workspace Entry: /Users/mc/dev/Loom-WI-1735-ship-contract
- Recovery Entry: .loom/progress/WI-1735.md
- Review Entry: .loom/reviews/WI-1735.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper; git diff --check; python3 tools/loom.py pr metadata-preflight 1744 --surface merge_ready --item WI-1735 --issue 1735 --branch work/1735-ship-contract --head-sha a195245d463a62bde522919ac8eccc38d3d2e9b9 --json --full-output
- Closing Condition: PR #1744 is merged, issue #1735 is closed, and closeout consumes PR, issue, branch, target branch, hosted checks, and repo carrier readback.
- Current Checkpoint: build
- Current Stop: Implementation complete for #1735; PR #1744 is open and waiting for merge gate/review consumption.
- Next Step: Consume current-head review and hosted checks, then merge PR #1744 and close out issue #1735.
- Blockers: None recorded
- Latest Validation Summary: 2026-06-23 local validation passed: PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper; git diff --check; PR metadata preflight for #1744 passed at head a195245d463a62bde522919ac8eccc38d3d2e9b9.
- Recovery Boundary: WI-1735 owns ship contract docs and ship-wrapper contract checks only; no runtime repair-chain implementation or closeout permission changes.
- Current Lane: ship-contract

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1713 build started in issue-scoped worktree `work/1713-plugin-release-metadata`.
- Logs Entry: Local validation output retained in this Codex thread and summarized in `.loom/progress/WI-1713.md`.
- Diagnostics Entry: `x-loom.plugin_payload_hash` is normalized during digest computation; other plugin manifest metadata remains part of the payload evidence.
- Verification Entry: Targeted checks, suite validation, build flow, version readback, package checks, CLI contract aggregate checks, review records, shadow parity, adopt verify, and governance profile status passed before PR creation.
- Lane Entry: plugin-release-metadata

## Sources

- Static Truth: .loom/work-items/WI-1735.md
- Dynamic Truth: .loom/progress/WI-1735.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
