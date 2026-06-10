# Current Status

## Derived Fact Chain View

- Item ID: WI-1250
- Goal: Split review-run fixtures into stable named regression groups for daily-execution-cli diagnostics while preserving full review-run coverage.
- Scope: Issue #1250 / PR #1411 only: review-run fixture grouping labels, diagnostics, synchronized loom_check runtime copies, demo metadata, and regression-surface inventory evidence; no #1249 label rename, no #1252 snapshot/bootstrap reuse, no #1251 fallback boundary change, no #1253 fast/full policy.
- Execution Path: issue #1250 -> branch work/1250-review-run-fixture-groups -> PR #1411 -> scheduler-owned review/pr-gate/controlled merge/closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1250.md
- Review Entry: .loom/reviews/WI-1250.json
- Validation Entry: git diff --check; py_compile_clean touched loom_check.py copies; skills_surface.py check; focused review-run group diagnostics probe; demo manifest json validation; examples/new-project loom_check source/consumer/contract-only checks; PR metadata preflight/readback; hosted checks
- Closing Condition: PR #1411 is reviewed/gated by the scheduler on the current head, merged through the controlled path, and #1250 closeout is consumed without changing adjacent Round 7 scopes.
- Current Checkpoint: build
- Current Stop: #1250 review-run fixture grouping implementation is pushed in PR #1411; branch-local WI-1250 carrier activation is in progress.
- Next Step: Scheduler owns current-head WI-1250 review and PR gate after carrier activation, metadata repair, push, and readback.
- Blockers: Scheduler-owned review/gate still pending; full review-run surface remains scheduler-owned/high-cost.
- Latest Validation Summary: Passed: git diff --check; py_compile_clean for touched loom_check.py copies; skills_surface.py check; focused review-run group diagnostics probe; demo manifest json validation; examples/new-project loom_check source/consumer/contract-only checks; PR metadata preflight/readback on old head; hosted py-compile/demo-bootstrap/repo-local-cli/loom-check/node-installer-gate/release-judgment passed on old head. Not run locally: full --source-surface review-run because high-cost/scheduler-owned.
- Recovery Boundary: WI-1250 only: review-run fixture grouping labels, diagnostics, synchronized loom_check runtime copies, demo metadata, regression-surface inventory evidence, branch-local carrier activation, and PR #1411 metadata repair.
- Current Lane: daily-cli-review-run-fixture-groups

## Runtime Evidence

- Run Entry: PR #1411 implementation head 79d2115c86b264fca409aca9462b58139aa259a8 passed local scoped validation before branch-local carrier activation; PR metadata must bind the pushed carrier head before scheduler gate.
- Logs Entry: worker thread 019eb04d-2478-7013-a751-03b1062ad36b and scheduler thread 019eaf94-f0bd-79a3-a396-83d6428b2777 command readbacks for WI-1250.
- Diagnostics Entry: WI-1250 splits review-run fixtures into stable named regression groups and synchronized runtime copies only; no #1249 label rename, #1252 snapshot/bootstrap reuse, #1251 fallback boundary change, or #1253 fast/full policy is included.
- Verification Entry: local validation passed for #1250 implementation before carrier activation; carrier activation validation includes git diff --check, carrier refresh dry-run, shadow parity, and PR metadata readback, while full review-run and current-head review/gate remain scheduler-owned.
- Lane Entry: daily-cli-review-run-fixture-groups

## Sources

- Static Truth: .loom/work-items/WI-1250.md
- Dynamic Truth: .loom/progress/WI-1250.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
