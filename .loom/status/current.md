# Current Status

## Derived Fact Chain View

- Item ID: WI-1393
- Goal: Split tools/check_release_surface.py release surface validation into named, targetable contract/workflow/guard surfaces while preserving aggregate release surface validation behavior.
- Scope: Issue #1393 only: tools/check_release_surface.py named release-doc-contract, release-workflow-contract, installer-sunset-guard, and forbidden-release-surface-patterns surfaces; Makefile aliases; docs/adoption/loom-cli-release-surface.md locator updates consuming the #1383 evidence contract; WI-1393 Loom carriers; scheduler-owned review/pr-gate/controlled merge/no_release closeout. No #1394 npm package split, #1395 installed/global CLI smoke, #1396 docs/evidence convergence, release publishing, package/runtime behavior, hosted workflow semantic changes, parent #1260 closeout, umbrella #1255 closeout, or Round 9+ scope.
- Execution Path: issue #1393 -> branch work/1393-release-surface-validator-split -> PR #1423 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1393.md
- Review Entry: .loom/reviews/WI-1393.json
- Validation Entry: git diff --check; tools/check_release_surface.py --list-surfaces and targeted #1393 surfaces; Makefile release-surface aliases; aggregate check_release_surface.py; check_npm_package.py compatibility; suite inspect/validate for WI-1393; fact-chain/state-check after scheduler activation; PR metadata preflight/readback; hosted checks
- Closing Condition: PR #1423 for #1393 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1393 is closed, and no_release closeout is consumable by #1260/#1255.
- Current Checkpoint: closed_out
- Current Stop: WI-1393 terminal closeout facts have been consumed: PR #1423 merged into `main` at 2026-06-10T22:11:32Z with merge commit `d459cc1488d2f6140925164fc4ab94fe54256e83`; issue #1393 closed at 2026-06-10T22:12:37Z; hosted required checks passed on head `b5f1f466aa04c59f1fbb5aed45c1cc49c9bcc46a`; no_release terminal metadata is recorded in `.loom/progress/WI-1393.md`.
- Next Step: None for WI-1393. Npm package validation surfaces, installed/global CLI smoke, and release/package convergence continue in #1394, #1395, and #1396; parent #1260 and umbrella #1255 consume this closeout later.
- Blockers: None
- Latest Validation Summary: Terminal closeout readback for WI-1393: PR #1423 merged at 2026-06-10T22:11:32Z with merge commit `d459cc1488d2f6140925164fc4ab94fe54256e83`; issue #1393 closed at 2026-06-10T22:12:37Z; hosted required checks passed on head `b5f1f466aa04c59f1fbb5aed45c1cc49c9bcc46a`; local `pr gate`, `controlled merge check/run`, `fact-chain`, `state-check`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, and `git diff --check` passed or are being revalidated on the closeout-only carrier branch; terminal no_release metadata is recorded.
- Recovery Boundary: WI-1393 is terminal. Do not reopen or modify implementation scope here; subsequent release/package stream work remains in #1394, #1395, #1396, parent #1260, and umbrella #1255.
- Current Lane: release-surface-validator-split

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1393 after PR #1423 merged into `main` at 2026-06-10T22:11:32Z with merge commit `d459cc1488d2f6140925164fc4ab94fe54256e83`; issue #1393 closed at 2026-06-10T22:12:37Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1393 waiting-scheduler-gate report T1393-waiting-scheduler-gate-202606102155, ran current-head review/gate/controlled-merge readback, manually reconciled the native dependency edge #1260 blocked by #1393 after the tool apply path reported unsupported `add_blocked_by`, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1393 adds named release surface validator targets while preserving aggregate release surface validation; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, workflow publish behavior, package runtime behavior, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1393: hosted required checks passed on PR #1423 head `b5f1f466aa04c59f1fbb5aed45c1cc49c9bcc46a`; PR #1423 merged at `d459cc1488d2f6140925164fc4ab94fe54256e83`; issue #1393 closed; reconciliation audit passes after native dependency readback; local `fact-chain`, `state-check`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, suite validation, and `git diff --check` pass or are being revalidated on the closeout-only carrier branch.
- Lane Entry: release-surface-validator-split

## Sources

- Static Truth: .loom/work-items/WI-1393.md
- Dynamic Truth: .loom/progress/WI-1393.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
