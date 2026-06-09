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
- Current Checkpoint: build checkpoint
- Current Stop: Repo-local-cli local validation aliases/docs and WI-1283 carriers are locally validated; branch is ready for commit, push, PR metadata readback, and hosted checks.
- Next Step: Commit and push the WI-1283 branch, create/update PR metadata, read back hosted checks, then stop at waiting-scheduler-gate.
- Blockers: None.
- Latest Validation Summary: 2026-06-09 T2 local validation: git diff --check passed; repo-local-cli group-order readback passed across Makefile variable, workflow steps, docs table, and repo-local-cli-full target order; make -n repo-local-cli-full showed the frozen order; make repo-local-cli-fast GROUP=workspace-locate passed; make repo-local-cli-full passed, including runtime-state-scene-conflict-negative fail-closed behavior where the underlying command returned result block and the Make target treated that as expected. WI-1283 carrier validation passed via loom_init fact-chain/verify, loom_flow purity-check, shadow-parity, adopt verify, suite evidence validate, and suite carrier validate; suite validate returned not_applicable by design with no blocking gaps. Scheduler-requested .loom/bin/__pycache__/ residue was removed and is absent from status.
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
