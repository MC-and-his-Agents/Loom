# Current Status

## Derived Fact Chain View

- Item ID: WI-1236
- Goal: Add HotCP-style regression fixtures for stale active closeout carriers.
- Scope: Issue #1236 only: extend `tools/check_cli_contract.py` governance-closeout fixtures and WI-1236 Loom carriers/spec evidence so stale active carrier closeout behavior is protected after #1235. Cover PR-merged/issue-closed carriers that still have non-terminal progress, fact-chain pointers to completed Work Items, workspace retire local-only semantics, carrier closeout sync repair behavior, root workspace naming, and retained historical item naming. Ownership constraints: main executor owns `tools/check_cli_contract.py` and WI-1236 `.loom/**` carriers/build evidence; sidecar inventory is read-only and integrated only through these carriers; no other Work Item files, release surfaces, runtime/schema/failure vocabulary, workflow behavior, or unrelated refactors are in scope. Excludes #1237 docs/help finalization, #1296 release/no-release closeout, parent #1228 closeout, Round 10, Round 11, Deferred roadmap, release/tag/npm actions, runtime/schema/failure vocabulary changes, and unrelated refactors.
- Execution Path: issue #1236 -> branch `work/1236-hotcp-regression-fixtures` -> focused governance-closeout fixture expansion -> local validation -> PR metadata/readback -> merge-ready gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1236.md
- Review Entry: .loom/reviews/WI-1236.json
- Validation Entry: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`; suite validate/evidence/carrier validate for WI-1236; fact-chain/status readback; PR metadata and hosted checks readback before merge.
- Closing Condition: PR for #1236 is pushed with HotCP-style stale active closeout regression fixtures, scoped WI-1236 carriers, clean local validation, PR metadata aligned to the branch head, passing required checks/gate, merge commit readback, and issue #1236 CLOSED/COMPLETED.
- Current Checkpoint: merge
- Current Stop: HotCP-style stale active closeout regression fixture, WI-1236 carriers, spec/implementation reviews, PR #1516 body readback, metadata preflight, and review gate are aligned for merge checkpoint consumption.
- Next Step: Refresh carrier/shadow for this merge checkpoint head, update PR #1516 metadata to the new head, rerun merge-ready and PR gate, then wait for hosted checks before controlled merge.
- Blockers: None
- Latest Validation Summary: 2026-06-16T14:21Z local freeze/readback before merge checkpoint carrier sync passed: `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1236 --dry-run`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py shadow-parity --target . --surface all --mode blocking`; PR #1516 body readback matched rendered metadata block for review and merge_ready preflight at head 031aada7dcbe96527201e16f9c9f74ebb452ad72; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py flow review --target . --item WI-1236 --pr 1516 --branch work/1236-hotcp-regression-fixtures` passed. Initial merge-ready and PR gate were classified as checkpoint drift only because the progress carrier still read `build`; this entry advances the carrier to `merge` for revalidation.
- Recovery Boundary: WI-1236/#1236 fixture inventory only. Consume stable #1235 behavior from origin/main merge commit 703feadf46162d7937ede040a098a013093b2c39; do not implement #1237 docs/help, #1296 release/no-release closeout, parent #1228 closeout, Round 10/11, Deferred roadmap, release/npm/live actions, VERSION/tag/GitHub Release/npm publish, workflow/runtime behavior changes, shared contract/schema/parser/failure vocabulary changes, or unrelated refactors.
- Current Lane: round-9-wi-8-hotcp-regression-fixtures

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: not_applicable
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1236.md
- Dynamic Truth: .loom/progress/WI-1236.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
