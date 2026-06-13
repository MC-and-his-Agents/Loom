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
- Current Stop: #1232 implementation, mainline reconciliation, PR #1473 metadata readback, and local validation are complete in worker scope; scheduler-owned review is in progress.
- Next Step: Scheduler records current-head spec and implementation review artifacts for WI-1232, refreshes any scheduler-owned shadow/gate evidence as required, then owns PR gate, merge, and closeout.
- Blockers: None
- Latest Validation Summary: 2026-06-13T07:21Z scheduler readback passed on branch `work/1232-idle-read-surfaces` at head `a80fc99fbb875e6ea7c5dccfda355b4d05195975`: live PR #1473 is open/non-draft and machine metadata binds WI-1232, branch, and head; `git diff --check origin/main...HEAD`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1232 --json`; `suite evidence validate`; `suite carrier validate`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py flow spec-review --target . --item WI-1232 --pr 1473 --branch work/1232-idle-read-surfaces`; and `flow review` found only missing scheduler-owned `.loom/reviews/WI-1232.spec.json` and `.loom/reviews/WI-1232.json`.
- Recovery Boundary: Continue only #1232 idle read-surface implementation, focused fixtures, synchronized runtime copies, scoped WI-1232 carriers, root current-item/status/shadow alignment for PR #1473, PR metadata/readback, and local validation. Do not implement #1233, #1234, #1235, #1236 beyond #1232 proof, #1237, #1296, Round 10, Round 11, Deferred roadmap, high-cost guardian/formal review, semantic review, review record, controlled merge, release, npm, tag, GitHub Release, live config mutation, or shared contract/schema/failure vocabulary changes.
- Current Lane: round-9-wi-4-idle-read-surfaces

## Runtime Evidence

- Run Entry: Scheduler thread `019ebecb-4123-7600-9527-6616c5e94d84` consumed worker recovery result, merged latest `origin/main` closeout carrier facts into PR #1473 branch, and is preparing exact-head review artifacts for WI-1232.
- Logs Entry: Worksite `/Users/mc/.codex/worktrees/c98a/Loom` on branch `work/1232-idle-read-surfaces`; branch is reconciled with current `origin/main`; correction scope is limited to WI-1232 review/gate readiness after #1234 closeout landed on main.
- Diagnostics Entry: Non-review blockers are clear locally; scheduler-owned review is recording exact-head `.loom/reviews/WI-1232.spec.json` and `.loom/reviews/WI-1232.json` before PR gate consumption.
- Verification Entry: Current validation evidence: fact-chain, state-check, suite validate/evidence/carrier validate, PR metadata readback, and scheduler flow spec-review/review readback passed except for missing review artifacts.
- Lane Entry: round-9-wi-4-idle-read-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1232.md
- Dynamic Truth: .loom/progress/WI-1232.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
