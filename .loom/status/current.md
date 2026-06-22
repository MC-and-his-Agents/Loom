# Current Status

## Derived Fact Chain View

- Item ID: WI-1715
- Goal: Report CLI and Codex plugin payload freshness from `loom version`, `loom doctor`, and `loom upgrade-plan`.
- Scope: Issue #1715 only. Update `tools/loom.py`, focused CLI contract checks, and WI-1715 carriers. Non-goals: no plugin refresh implementation, no release execution, no single SKILL install, no legacy installer changes.
- Execution Path: issue #1715 -> branch `work/1715-freshness-reporting` -> worktree `.loom/..` -> targeted validation -> PR -> controlled merge -> closeout.
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1715.md
- Review Entry: .loom/reviews/WI-1715.json
- Validation Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `git diff --check`.
- Closing Condition: PR for `work/1715-freshness-reporting` is merged into `main`, issue #1715 is closed, and closeout consumes PR, issue, hosted checks, target branch, and repo carrier readback.
- Current Checkpoint: merge
- Current Stop: PR #1750 is ready for merge gate evaluation at head cd095c4d724356db4a71ae764a3e4c10376c8328 after portable workspace-entry repair, PR metadata readback, authored review, and CI fixture regression fixes.
- Next Step: Run PR gate, hosted checks, controlled merge, and closeout for WI-1715.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 local checks passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py --surface governance-closeout; python3 tools/check_cli_contract.py --surface aggregate; git diff --check; python3 tools/loom.py suite validate --target . --item WI-1715 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1715 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1715 --json; python3 tools/loom.py fact-chain --target . --item WI-1715 --json; local PR gate passed at head f1d5efe before portable workspace-entry repair.
- Recovery Boundary: WI-1715 owns freshness reporting in `version`, `doctor`, `host doctor`, and `upgrade-plan`. It does not implement plugin refresh UX (#1716), broad fixtures (#1717), or v0.19.0 release closeout (#1718).
- Current Lane: freshness-reporting

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1715 build started in issue-scoped worktree `work/1715-freshness-reporting`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1715.md`.
- Diagnostics Entry: `loom version --json` reports `version_freshness` with CLI, plugin payload, surface compatibility, and next action.
- Verification Entry: Targeted CLI contract, py_compile, direct JSON assertions, and diff checks passed before suite validation.
- Lane Entry: freshness-reporting

## Sources

- Static Truth: .loom/work-items/WI-1715.md
- Dynamic Truth: .loom/progress/WI-1715.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
