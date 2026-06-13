# Current Status

## Derived Fact Chain View

- Item ID: WI-1233
- Goal: Enhance stale active workspace diagnostics so Loom can distinguish host-complete carrier drift from a live shared-workspace conflict.
- Scope: Issue #1233 only: add and consume the active workspace diagnostics classification `carrier_closeout_required` when GitHub issue or PR host truth is closed, completed, or merged while the repo recovery carrier remains non-terminal. Preserve existing `stale_carrier`, `shared_workspace_conflict`, and metadata/status boolean `closeout_required` semantics. Keep true multi-active workspace conflicts blocking and point host-complete carrier drift remediation to carrier closeout sync rather than workspace retire.
- Execution Path: issue #1233 -> branch `work/1233-host-truth-diagnostics-recovery` -> PR for diagnostics vocabulary/source/runtime copies/tests/carriers -> scheduler-owned review and merge gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1233.md
- Review Entry: .loom/reviews/WI-1233.json
- Validation Entry: `git diff --check`; Python compile for touched Python files; focused retire workspace fixture covering `carrier_closeout_required`, preserved `stale_carrier`, and preserved `shared_workspace_conflict`; suite/carrier validation where applicable.
- Closing Condition: The #1233 PR exposes `carrier_closeout_required` for host-complete non-terminal carriers, preserves existing active workspace classifications, passes focused local validation and metadata readback, and stops at `waiting-scheduler-gate` for scheduler-owned review/gate.
- Current Checkpoint: build
- Current Stop: Implementing #1233 host-truth active workspace diagnostics on branch `work/1233-host-truth-diagnostics-recovery` under contract lane grant `watcher-contract-lane-grant-round9-T1233-carrier-closeout-required-202606130238`.
- Next Step: Finish source/runtime copy synchronization, focused validation, PR metadata readback, push, PR creation/update, hosted checks readback, and scheduler-readable waiting-scheduler-gate report.
- Blockers: None at implementation start.
- Latest Validation Summary: 2026-06-13T03:05Z local validation passed on branch `work/1233-host-truth-diagnostics-recovery`: `git diff --check`; `make loom-demo-new-project-check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py .loom/bin/loom_flow.py .loom/bin/loom_check.py src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py skills/loom-*/.loom-runtime/shared/scripts/loom_flow.py skills/loom-*/.loom-runtime/shared/scripts/loom_check.py examples/new-project/.loom/bin/loom_flow.py examples/new-project/.loom/bin/loom_check.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface retire-workspace .`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1233 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1233 --json`. PR #1474 metadata preflight/readback passed for rendered body and GitHub body machine block after initial PR creation; PR body will be refreshed to the final amended head before scheduler gate. Startup readback: worksite `/Users/mc/.codex/worktrees/973a/Loom`, base `origin/main` at `a1712a017d597b22a9bf08ca5fd991d78127acf8`, issue #1233 OPEN, no open PR for branch before implementation.
- Recovery Boundary: #1233 diagnostics vocabulary only: `carrier_closeout_required` for host-complete carrier drift, preserving `stale_carrier`, `shared_workspace_conflict`, and `closeout_required` semantics. No merge, guardian/formal review, release, live config mutation, sibling issue implementation, or downstream issue writes.
- Current Lane: contract_lane

## Runtime Evidence

- Run Entry: Worker thread `019ebedc-e585-77a3-ac6e-e4e9a7b8490e` accepted scheduler instruction `T1233R-recovery-202606130242` for issue #1233 on branch `work/1233-host-truth-diagnostics-recovery`.
- Logs Entry: Worksite `/Users/mc/.codex/worktrees/973a/Loom`; base `origin/main` at `a1712a017d597b22a9bf08ca5fd991d78127acf8`; contract lane grant `watcher-contract-lane-grant-round9-T1233-carrier-closeout-required-202606130238`.
- Diagnostics Entry: Implementation scope is limited to active workspace diagnostics classification `carrier_closeout_required` for host-complete carrier drift and maintained runtime/test/doc copies.
- Verification Entry: Startup readback commands completed before editing: `pwd`, `git rev-parse --show-toplevel`, `git branch --show-current`, `git rev-parse HEAD`, `git merge-base HEAD origin/main`, `git status --short --branch`, `gh issue view 1233`, and `gh pr list --state open --head work/1233-host-truth-diagnostics-recovery`. Local implementation validation passed: `git diff --check`; `make loom-demo-new-project-check`; focused Python compile for synchronized `loom_flow.py` / `loom_check.py` copies including demo runtime; `tools/loom_check.py --profile source --source-surface retire-workspace .`; `tools/loom.py suite validate --target . --item WI-1233 --json`; `tools/loom.py suite carrier validate --target . --item WI-1233 --json`.
- Lane Entry: contract_lane

## Sources

- Static Truth: .loom/work-items/WI-1233.md
- Dynamic Truth: .loom/progress/WI-1233.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target . --item WI-1233
