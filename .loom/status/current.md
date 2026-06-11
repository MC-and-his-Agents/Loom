# Current Status

## Derived Fact Chain View

- Item ID: WI-1290
- Goal: Freeze the repo companion / guardian adapter integration contract that Round 11 fixtures and docs/release convergence can consume without redefining Loom core review/head-binding semantics.
- Scope: Issue #1290 only: docs/adoption companion/guardian adapter contract wording, WI-1290 Loom carriers, docs-only formal-suite not_applicable carrier, scheduler-owned review artifact, and PR metadata for this branch. No runtime/parser/checker changes, no fixture implementation for #1292, no docs/release convergence for #1293, no Makefile or generated runtime edits beyond consuming already-merged main, and no parent #1285/#1293 closeout carrier.
- Execution Path: issue #1290 -> branch work/1290-adapter-contract -> PR #1439 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1290.md
- Review Entry: .loom/reviews/WI-1290.json
- Validation Entry: git diff --check; focused contract/readback scan for allow|block|fallback, evidence locator, merge semantics, diagnostics, and repo examples; python3 tools/loom.py suite inspect --target . --item WI-1290 --json; suite validate for WI-1290 not_applicable; PR metadata preflight/readback; hosted checks readback
- Closing Condition: PR #1439 for #1290 is reviewed and gated by the scheduler on the current head, merged through the controlled path, issue #1290 is closed by the PR, and #1292/#1293 can consume the frozen adapter contract without redefining Loom core semantic_review_disposition or PR head binding.
- Current Checkpoint: closed_out
- Current Stop: WI-1290 terminal closeout consumed: PR #1439 merged into main at 2026-06-11T06:46:29Z with merge commit 19452e5a215c4d4c6b7125ef6893fe9e993f3470; issue #1290 closed as COMPLETED at 2026-06-11T06:46:30Z; controlled merge, closeout check, and carrier closeout-sync passed; no release is required for this docs-only adapter contract freeze.
- Next Step: No further #1290 action. Watcher may independently consider successor #1292 after verifying #1290 completion.
- Blockers: None
- Latest Validation Summary: 2026-06-11 scheduler validation: git diff --check passed; fact-chain and state-check passed for WI-1290; checkpoint build passed; focused rg readback confirmed guardian_adapters, allow/block/fallback, structured evidence locator requirements, deterministic merge semantics, diagnostics taxonomy, and HotCP/WebEnvoy/Syvert examples; suite inspect returned result=pass and suite validate returned expected result=not_applicable with no blocking gaps; PR #1439 body metadata preflight/readback passed for head 527dfaa4432ee77db8022e7d932ca7bf90f237de, then scheduler refreshed carrier/review evidence through local head 579a0611845283d895b94684646a8ec7f7659874; final PR metadata must be rebound after the merge-checkpoint/review-only commits.
- Recovery Boundary: Terminal closeout carrier/status sync only for WI-1290. Do not implement #1292/#1293, parent #1285 closeout, runtime/parser/checker changes, release artifacts, or external runtime behavior.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1399 after PR #1432 merged into `main` at 2026-06-11T05:41:50Z with merge commit `13e1280b24ca0a21be0f602b525038fad1fce96f`; issue #1399 closed at 2026-06-11T05:46:25Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1399 waiting-scheduler-gate report T1399-waiting-scheduler-gate-202606110259, ran current-head review/gate/controlled-merge readback, used Loom reconciliation audit and GraphQL `addBlockedBy` to reconcile the native dependency edge #1261 blocked by #1399 after dry-run proof, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1399 adds a named skills launcher-smoke validation surface with per-skill filtering while preserving #1397 docs-reference-sync/generated-tree-drift, #1398 package-metadata/cache-artifacts, and aggregate skills validation behavior; terminal closeout records no_release because no VERSION, tag, release artifact, package publish, hosted workflow semantics, runtime behavior, permissions, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1399: hosted required checks passed on PR #1432 head `60267dc127669a0fc7490976b53310e49e815c02`; PR #1432 merged at `13e1280b24ca0a21be0f602b525038fad1fce96f`; issue #1399 closed; reconciliation audit passes after native dependency readback; local `closeout check`, `fact-chain`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, `suite validate` not_applicable with blocking_gaps=[], and `git diff --check` pass on the closeout-only carrier branch.
- Lane Entry: skills-launcher-smoke-surface

## Sources

- Static Truth: .loom/work-items/WI-1290.md
- Dynamic Truth: .loom/progress/WI-1290.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
