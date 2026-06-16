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
- Current Checkpoint: build
- Current Stop: HotCP-style stale active closeout regression fixture, WI-1236 carriers, shadow refresh, build evidence, build flow, focused governance-closeout validation, and deterministic review-readiness evidence are in place.
- Next Step: Amend the stable WI-1236 head with review-readiness evidence, then enter pre-review/review and merge-ready for PR #1236.
- Blockers: None
- Latest Validation Summary: 2026-06-16T14:11Z final local validation before pre-review on branch work/1236-hotcp-regression-fixtures passed: carrier refresh dry-run pass, shadow-parity pass, suite validate/evidence/carrier validate pass, `git diff --check` pass, `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/check_cli_contract.py` pass, `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py flow build --target . --item WI-1236 --build-evidence .loom/runtime/build/WI-1236.json` pass, `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout` passed in 97.63s, `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check` passed, and `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only` passed.
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
