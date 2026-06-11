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
- Current Checkpoint: build
- Current Stop: Scheduler consumed worker output and recovered stalled worker state. PR #1439 is open on branch work/1290-adapter-contract at head 24487546959a75cde2915d7c48199b06130db571 after refreshing from origin/main 728e467073607d07e2e526121e87a628b4691357. PR body machine carrier readback and local metadata preflight pass for the current head. Scope diff remains limited to docs/adoption/repo-companion-contract.md and WI-1290 carriers.
- Next Step: Record scheduler-owned semantic review for the current head, run PR gate/hosted check readback, then controlled merge and closeout if gates pass.
- Blockers: None
- Latest Validation Summary: 2026-06-11 scheduler validation on head 24487546959a75cde2915d7c48199b06130db571: git diff --check origin/main...HEAD passed; diff is limited to docs/adoption/repo-companion-contract.md, .loom/work-items/WI-1290.md, .loom/progress/WI-1290.md, and .loom/specs/WI-1290/spec.md; focused rg readback confirmed guardian_adapters, allow/block/fallback, structured evidence locator requirements, deterministic merge semantics, diagnostics taxonomy, and HotCP/WebEnvoy/Syvert examples; suite inspect returned result=pass and suite validate returned expected result=not_applicable with no blocking gaps; PR #1439 body readback matches head 24487546959a75cde2915d7c48199b06130db571; python3 tools/loom.py pr metadata-preflight --surface merge_ready --body-file .loom/tmp/WI-1290-pr-body-readback.md --json returned result=pass.
- Recovery Boundary: WI-1290 only owns the adapter contract wording, WI-1290 carriers, scheduler-owned review artifact, and PR metadata/head binding. Do not implement #1292 fixtures, #1293 release/docs convergence, runtime/parser/checker code, parent #1285/#1293 closeout, or unrelated shared carrier changes.
- Current Lane: adapter-contract-freeze

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
