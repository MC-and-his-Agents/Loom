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
- Current Checkpoint: merge
- Current Stop: #1233 implementation, runtime copy propagation, root fact-chain carrier sync, mainline reconciliation, PR #1474 metadata readback, local validation, and scheduler-owned spec/implementation review records are complete; merge gate consumption is in progress.
- Next Step: Scheduler consumes local PR gate / merge-ready and hosted checks for the current head, then requests exact watcher merge_lane if all gate evidence is green.
- Blockers: None
- Latest Validation Summary: 2026-06-13T07:40Z scheduler review/gate recovery passed on branch `work/1233-host-truth-diagnostics-recovery`: live PR #1474 is open/non-draft and machine metadata was refreshed through review-carrier head `df0d42a9cacaadfe0172b4cc859ba49c0051fe72`; `git diff --check`; suite validate/evidence/carrier validate; PR metadata preflight; scheduler-authored `.loom/reviews/WI-1233.spec.json`; scheduler-authored `.loom/reviews/WI-1233.json`; and local PR gate readback consumed review records with no missing inputs after PR body Branch / Head SHA metadata was restored.
- Recovery Boundary: #1233 diagnostics vocabulary only: `carrier_closeout_required` for host-complete carrier drift, preserving `stale_carrier`, `shared_workspace_conflict`, and `closeout_required` semantics. No merge, guardian/formal review, release, live config mutation, sibling issue implementation, or downstream issue writes.
- Current Lane: contract_lane

## Runtime Evidence

- Run Entry: Worker thread `019ebedc-e585-77a3-ac6e-e4e9a7b8490e` accepted scheduler instruction `T1233R-recovery-202606130242` for issue #1233 on branch `work/1233-host-truth-diagnostics-recovery`.
- Logs Entry: Worksite `/Users/mc/.codex/worktrees/973a/Loom`; base `origin/main` at `a1712a017d597b22a9bf08ca5fd991d78127acf8`; contract lane grant `watcher-contract-lane-grant-round9-T1233-carrier-closeout-required-202606130238`.
- Diagnostics Entry: Implementation scope remains limited to active workspace diagnostics classification `carrier_closeout_required`; non-review and review blockers are clear locally, and scheduler is consuming merge gate evidence for PR #1474.
- Verification Entry: Current validation evidence: fact-chain, state-check, suite validate/evidence/carrier validate, PR metadata readback, scheduler-authored spec/implementation review records, and local PR gate review consumption.
- Lane Entry: contract_lane

## Sources

- Static Truth: .loom/work-items/WI-1233.md
- Dynamic Truth: .loom/progress/WI-1233.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
