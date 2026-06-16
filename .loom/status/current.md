# Current Status

## Derived Fact Chain View

- Item ID: WI-1237
- Goal: Update README, methodology docs, CLI help, and release surface for idle closeout sync.
- Scope: Issue #1237 only: document idle/no-active-item recovery for HotCP-style stale carriers, distinguish `workspace retire` local-only cleanup from host closeout sync and `carrier closeout-sync`, update root CLI help summaries for those lifecycle layers, and extend release-surface validation so release/no-release closeout can consume the new command names and fixture story. Consume completed #1235 and #1236 behavior from origin/main. Ownership constraints: main executor owns the listed docs/help/checker files and WI-1237 `.loom/**` carriers only. Do not change runtime semantics, schema, parser, failure vocabulary, release workflows, package payload behavior, Round 10/11, Deferred roadmap, #1296 release/no-release closeout, parent #1228 closeout, or unrelated files.
- Execution Path: issue #1237 -> branch `work/1237-docs-help-closeout` -> docs/help/release-surface update -> local validation -> PR metadata/readback -> merge-ready gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1237.md
- Review Entry: .loom/reviews/WI-1237.json
- Validation Entry: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_release_surface.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py help --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py --surface release-doc-contract`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`; suite validate/evidence/carrier validate for WI-1237; fact-chain/status readback; PR metadata and hosted checks readback before merge.
- Closing Condition: PR for #1237 is pushed with docs/help/release-surface evidence aligned to #1235/#1236 stable behavior, scoped WI-1237 carriers, clean local validation, PR metadata aligned to branch head, passing required checks/gate, merge commit readback, and issue #1237 CLOSED/COMPLETED.
- Current Checkpoint: merge
- Current Stop: README, harness methodology docs, CLI help summaries, release-surface checker coverage, WI-1237 suite carriers, fact-chain, shadow parity, release surface checks, skills release-check, full CLI contract validation, pre-review, spec-review, and implementation review are passing locally; PR metadata, readback, hosted checks, merge-ready, merge, and closeout remain.
- Next Step: Create and preflight PR metadata against the current head, push branch, create/read back PR, run freeze checklist and merge-ready gate, then wait for hosted checks before merge.
- Blockers: None
- Latest Validation Summary: 2026-06-16T15:33Z local and host validation passed: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_release_surface.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py help --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py --surface release-doc-contract`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`; suite validate/evidence/carrier for WI-1237; fact-chain readback for WI-1237 at checkpoint merge; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target .`; full `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py` passed all 6 surfaces in 288.09s; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only` passed; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py flow build --target . --item WI-1237`, `flow pre-review`, `flow spec-review`, and post-PR `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py flow review --target . --item WI-1237 --pr 1518 --branch work/1237-docs-help-closeout --issue 1237` passed; PR #1518 GitHub readback is OPEN/ready with head `8792fee936436d4b3700a863fe84d5e25a760190`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py pr-metadata preflight --target . --surface merge_ready --pr 1518 --head-sha 8792fee936436d4b3700a863fe84d5e25a760190 --branch work/1237-docs-help-closeout` passed; GraphQL removed stale #1237 blocked-by edges to CLOSED #1232, #1233, #1234, #1235, and #1236, then readback returned `blockedBy.nodes=[]` and `blocking.nodes=[#1228,#1296]`.
- Recovery Boundary: WI-1237/#1237 docs/help/release-surface closeout only. Consume #1235 merge commit 703feadf46162d7937ede040a098a013093b2c39 and #1236 closeout merge commit 47083d932490b76a49f97d9a0cb307134582282b; do not implement #1296 release/no-release closeout, parent #1228 closeout, Round 10/11, Deferred roadmap, release/npm/live actions, VERSION/tag/GitHub Release/npm publish, runtime behavior, shared schema/parser/failure vocabulary changes, or unrelated refactors.
- Current Lane: round-9-wi-9-docs-help-closeout

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: not_applicable
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1237.md
- Dynamic Truth: .loom/progress/WI-1237.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
