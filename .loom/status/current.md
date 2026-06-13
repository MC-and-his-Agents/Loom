# Current Status

## Derived Fact Chain View

- Item ID: WI-1232
- Goal: Teach Loom fact-chain, status, and governance read surfaces to consume idle/no-active-item state without weakening active Work Item fail-closed checks.
- Scope: Issue #1232 only: update fact-chain inspection, status reporting, governance carrier summaries, focused CLI contract fixtures, synchronized runtime copies, and WI-1232 carriers. Excludes #1233 host-truth diagnostics, #1234 retained lookup, #1235 repair/apply, #1236 fixture expansion beyond #1232 proof, #1237 docs/help finalization, #1296 release, Round 10, Round 11, Deferred roadmap, high-cost guardian/formal review, controlled merge, release, npm, tag, GitHub Release, live config mutation, and shared contract/schema/failure vocabulary changes.
- Execution Path: issue #1232 -> branch `work/1232-idle-read-surfaces` -> idle read-surface implementation and focused fixtures -> local validation -> PR metadata/readback -> scheduler-owned gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1232.md
- Review Entry: .loom/reviews/WI-1232.json
- Validation Entry: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py` on touched Python files; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_status.py --target .`; PR metadata preflight/readback; hosted checks readback if available.
- Closing Condition: PR for #1232 is pushed with idle fact-chain/status/governance read surfaces, active locator/stale-status fail-closed fixture coverage, scoped WI-1232 carriers, clean local validation, PR metadata aligned to the branch head, and worker stops at scheduler-owned gate.
- Current Checkpoint: build
- Current Stop: Review prerequisite recovery for PR #1473 is in progress on branch `work/1232-idle-read-surfaces`: local `pr-gate check` and `flow merge-ready` confirmed the remaining non-review formal suite prerequisite was missing `.loom/specs/WI-1232/implementation-contract.md`; `.loom/reviews/WI-1232.json` remains scheduler-owned and intentionally absent.
- Next Step: Commit and push the minimal implementation contract/carrier update, update/read back PR #1473 metadata for the new head, mark PR #1473 ready-for-review only after local draft/metadata/contract blockers are cleared, read hosted checks, then stop for scheduler-owned exact-head review and gate decision.
- Blockers: Scheduler-owned current-head review/gate remains pending after non-review prerequisites are cleared; no local #1232 idle behavior blocker is known.
- Latest Validation Summary: 2026-06-13 review-prereq recovery consumed local gate readback on head `f1170d8ed1bcc88eceae3ea1709bae2bcba1070a`: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1232 --json`, `suite evidence validate`, and `suite carrier validate` passed; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py pr-metadata preflight --target . --surface merge_ready --pr 1473 --head-sha f1170d8ed1bcc88eceae3ea1709bae2bcba1070a --branch work/1232-idle-read-surfaces` passed; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py pr-gate check --target . --pr 1473 --head-sha f1170d8ed1bcc88eceae3ea1709bae2bcba1070a --branch work/1232-idle-read-surfaces` and `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py flow merge-ready --target . --item WI-1232 --pr 1473 --branch work/1232-idle-read-surfaces` confirmed the non-review contract blocker `missing formal spec suite file: .loom/specs/WI-1232/implementation-contract.md`, plus PR draft and scheduler-owned missing `.loom/reviews/WI-1232.json`. This recovery adds only the minimal implementation contract artifact bound to existing #1232 spec/plan/evidence and does not create review artifacts or expand suite scope.
- Recovery Boundary: Continue only #1232 idle read-surface implementation, focused fixtures, synchronized runtime copies, scoped WI-1232 carriers, root current-item/status/shadow alignment for PR #1473, PR metadata/readback, and local validation. Do not implement #1233, #1234, #1235, #1236 beyond #1232 proof, #1237, #1296, Round 10, Round 11, Deferred roadmap, high-cost guardian/formal review, semantic review, review record, controlled merge, release, npm, tag, GitHub Release, live config mutation, or shared contract/schema/failure vocabulary changes.
- Current Lane: round-9-wi-4-idle-read-surfaces

## Runtime Evidence

- Run Entry: Worker T1232 is clearing PR #1473 non-review merge-gate prerequisites in scheduler thread `019ebecb-4123-7600-9527-6616c5e94d84` after local gate readback showed missing `.loom/specs/WI-1232/implementation-contract.md`.
- Logs Entry: Worksite `/Users/mc/.codex/worktrees/c98a/Loom` on branch `work/1232-idle-read-surfaces`; correction scope is limited to the minimal WI-1232 implementation contract, carrier/status metadata, shadow refresh if required, PR metadata/readback, and PR ready-for-review state.
- Diagnostics Entry: The current non-review blocker is the formal suite contract prerequisite; `.loom/reviews/WI-1232.json` and `.loom/reviews/WI-1232.spec.json` remain scheduler-owned and intentionally absent until exact-head review authorization.
- Verification Entry: Required correction validation is `git diff --check origin/main...HEAD`, Python compile over changed Python files if any, fact-chain/state-check, suite validate/evidence/carrier validate, carrier refresh dry-run, shadow parity, PR metadata preflight/readback, local pr-gate/root-self equivalent checks, and hosted checks readback before scheduler handoff.
- Lane Entry: round-9-wi-4-idle-read-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1232.md
- Dynamic Truth: .loom/progress/WI-1232.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
