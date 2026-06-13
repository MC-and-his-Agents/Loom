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
- Current Stop: Mainline reconciliation is ready for PR metadata refresh on branch `work/1232-idle-read-surfaces` after merging current `origin/main` closeout carrier facts; the branch keeps WI-1232 as the active carrier and treats WI-1234 as terminal stale carrier evidence.
- Next Step: Record scheduler-owned spec and implementation review artifacts for the current head, update/read back PR #1473 metadata after the review-carrier commit, rerun local PR gate/merge-ready checks, push, and consume hosted checks before requesting any merge lane.
- Blockers: Scheduler-owned exact-head review artifacts and hosted gate consumption remain pending; no local #1232 idle behavior, formal-suite, metadata, shadow, or base-alignment blocker is known.
- Latest Validation Summary: 2026-06-13 mainline reconciliation passed local checks after merging `origin/main` into `work/1232-idle-read-surfaces`: `git diff --check origin/main...HEAD`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py $(git diff --name-only origin/main...HEAD -- '*.py')`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1232 --json`; `suite evidence validate`; `suite carrier validate`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1232 --dry-run`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --mode validation-only`; and `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1232`. Local PR gate/merge-ready remain expected to block only on scheduler-owned `.loom/reviews/WI-1232.spec.json` and `.loom/reviews/WI-1232.json`.
- Recovery Boundary: Continue only #1232 idle read-surface implementation, focused fixtures, synchronized runtime copies, scoped WI-1232 carriers, root current-item/status/shadow alignment for PR #1473, PR metadata/readback, and local validation. Do not implement #1233, #1234, #1235, #1236 beyond #1232 proof, #1237, #1296, Round 10, Round 11, Deferred roadmap, high-cost guardian/formal review, semantic review, review record, controlled merge, release, npm, tag, GitHub Release, live config mutation, or shared contract/schema/failure vocabulary changes.
- Current Lane: round-9-wi-4-idle-read-surfaces

## Runtime Evidence

- Run Entry: Scheduler thread `019ebecb-4123-7600-9527-6616c5e94d84` consumed worker recovery result, merged latest `origin/main` closeout carrier facts into PR #1473 branch, and is preparing exact-head review artifacts for WI-1232.
- Logs Entry: Worksite `/Users/mc/.codex/worktrees/c98a/Loom` on branch `work/1232-idle-read-surfaces`; branch is reconciled with current `origin/main`; correction scope is limited to WI-1232 review/gate readiness after #1234 closeout landed on main.
- Diagnostics Entry: Non-review blockers are clear locally; remaining required inputs are scheduler-owned `.loom/reviews/WI-1232.spec.json` and `.loom/reviews/WI-1232.json`, then PR metadata/readback and hosted gate consumption on the resulting head.
- Verification Entry: Current validation evidence: fact-chain, state-check, suite validate/evidence/carrier validate, py_compile_clean, carrier refresh dry-run, and shadow parity validation-only passed after mainline reconciliation.
- Lane Entry: round-9-wi-4-idle-read-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1232.md
- Dynamic Truth: .loom/progress/WI-1232.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
