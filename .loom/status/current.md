# Current Status

## Derived Fact Chain View

- Item ID: WI-1851
- Goal: v0.25.0 shift-left readiness and task-oriented CLI guidance
- Scope: Implement local readiness drift classification, write-after-readback/preflight, closeout/carrier-sync suite preservation, and task-oriented help/README/SKILL guidance for #1851/#1852/#1853/#1850/#1854.
- Execution Path: minimal suite; implementation PR then release PR
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1851.md
- Review Entry: .loom/reviews/WI-1851.json
- Validation Entry: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface aggregate; python3 tools/loom.py skills check --target . --json; python3 tools/check_npm_package.py --surface plugin-payload-hash
- Closing Condition: PR merged, no-release closeout evidence consumed for implementation, then v0.25.0 release/readback/terminal carrier closeout in #1855.
- Current Checkpoint: merge
- Current Stop: Release-readback contract blocker is fixed at reviewed code head e5c1e6be2dcd2afbfb6740b44c8f76e800bd8d5a; review/spec-review now approve that head.
- Next Step: Refresh closeout/merge-ready shadow, commit carrier-only updates, push, update PR metadata to the final head, then rerun PR gate and hosted checks.
- Blockers: None recorded.
- Latest Validation Summary: Passed for reviewed code head e5c1e6be2dcd2afbfb6740b44c8f76e800bd8d5a: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface release-readback; python3 tools/check_cli_contract.py --surface pr-metadata; git diff --check. Previous broader validation passed before the focused release-readback repair; final PR gate and hosted checks must be rerun after carrier refresh.
- Recovery Boundary: .loom/reviews/WI-1851.json; .loom/reviews/WI-1851.spec.json; .loom/progress/WI-1851.md; .loom/status/current.md
- Current Lane: merge-gate-prep

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1851 work is active in `/Users/mc/dev/Loom.worktrees/1851-shift-left-readiness` on branch `work/1851-shift-left-readiness`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1851.md`.
- Diagnostics Entry: Hosted `release-judgment` exposed that agent-safe output was dropping the `readiness` envelope; `tools/loom.py` now preserves readiness in compact agent-safe output.
- Verification Entry: `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface release-readback`; `python3 tools/check_cli_contract.py --surface pr-metadata`; `git diff --check`.
- Lane Entry: merge-gate-prep

## Sources

- Static Truth: .loom/work-items/WI-1851.md
- Dynamic Truth: .loom/progress/WI-1851.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
