# Current Status

## Derived Fact Chain View

- Item ID: WI-1283
- Goal: Add repo-local-cli local validation aliases and documentation so maintainers can reproduce the frozen CI command groups locally.
- Scope: Issue #1283 only: Makefile repo-local-cli local validation aliases and narrow docs that distinguish fast versus full validation, preserve #1282 group names/order, keep runtime-state scene conflict negative check fail-closed, and do not weaken merge-ready or loom-check required gates. Excluded: workflow edits, #1284 evidence/closeout, #1259 closeout, generated runtime, release/package behavior, and unrelated tools.
- Execution Path: issue #1283 -> branch work/1283-repo-local-cli-local-validation -> #1282 command contract readback -> Makefile aliases/docs -> local fast/full replay validation -> WI-1283 carrier/PR metadata -> scheduler-owned gate
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1283.md
- Review Entry: .loom/reviews/WI-1283.json
- Validation Entry: git diff --check; repo-local-cli group-order readback; make repo-local-cli-fast GROUP=workspace-locate; make repo-local-cli-full; fact-chain/verify/purity/shadow/adopt checks; PR metadata/head readback; hosted checks
- Closing Condition: Worker stops at waiting-scheduler-gate after clean local validation, PR metadata/head readback, and hosted checks; scheduler owns review/merge-ready/merge/closeout and issue #1283 closure.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-1283 local aliases/docs, PR metadata, hosted repo-local checks, and carrier readiness are prepared for scheduler-owned semantic review.
- Next Step: Scheduler records current-head semantic review disposition for WI-1283, then reruns pr-gate / merge-ready and proceeds to controlled merge only if gates pass.
- Blockers: None
- Latest Validation Summary: 2026-06-09 T2 gate-input readiness correction: official recovery writeback moved WI-1283 to merge checkpoint with Blockers: None and synchronized .loom/status/current.md; official carrier refresh updated .loom/shadow/merge-ready-loom.json and .loom/shadow/closeout-loom.json after status sha drift. Validation passed: git diff --check; loom_init fact-chain; loom_init verify; loom_flow purity-check; checkpoint build; shadow-parity --blocking; adopt verify. Final PR metadata, flow review, and pr-gate checks are expected to be clean except for scheduler-owned semantic_review_disposition, which T2 is forbidden to record.
- Recovery Boundary: WI-1283 only: Makefile repo-local-cli local validation aliases, narrow repo-local validation docs, WI-1283 carriers, and PR metadata. Do not edit workflow semantics, #1284 evidence/closeout, #1259 closeout, generated runtime, release/package behavior, Round 5, Round 7+, Deferred roadmap, or unrelated tools.
- Current Lane: repo-local-cli-surfaces

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: local command outputs in worker thread 019eab0f-b79e-7ab1-856e-205b0a288c41
- Diagnostics Entry: `installed-runtime` source surface added through canonical runtime and generated skills sync; no release/package/workflow behavior changes expected.
- Verification Entry: focused `installed-runtime`, `contract-only`, skills parity, compile, and diff checks passed; aggregate `source-self-fixture` consumed and passed `installed-runtime`; non-#1280 `review-run-fixture` residue is classified outside the WI-1280 blocker path.
- Lane Entry: source-self-installed-runtime-fixtures

## Sources

- Static Truth: .loom/work-items/WI-1283.md
- Dynamic Truth: .loom/progress/WI-1283.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
