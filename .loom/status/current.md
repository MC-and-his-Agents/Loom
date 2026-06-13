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
- Current Checkpoint: merge
- Current Stop: #1232 implementation, mainline reconciliation, PR #1473 metadata readback, local validation, and scheduler-owned spec/implementation review records are complete; merge gate consumption is in progress.
- Next Step: Scheduler consumes local PR gate / merge-ready and hosted checks for the current head, then requests exact watcher merge_lane if all gate evidence is green.
- Blockers: None
- Latest Validation Summary: 2026-06-13T07:40Z scheduler review/gate recovery passed on branch `work/1232-idle-read-surfaces`: live PR #1473 is open/non-draft and machine metadata was refreshed through review-carrier head `a6b95d328393e7bbb2e074ed09312600bbe88d68`; `git diff --check origin/main...HEAD`; suite validate/evidence/carrier validate; PR metadata preflight; scheduler-authored `.loom/reviews/WI-1232.spec.json`; scheduler-authored `.loom/reviews/WI-1232.json`; and local PR gate readback consumed review records with no missing inputs before falling back only because the carrier checkpoint still needed this merge-gate advancement.
- Recovery Boundary: Continue only #1232 idle read-surface implementation, focused fixtures, synchronized runtime copies, scoped WI-1232 carriers, root current-item/status/shadow alignment for PR #1473, PR metadata/readback, and local validation. Do not implement #1233, #1234, #1235, #1236 beyond #1232 proof, #1237, #1296, Round 10, Round 11, Deferred roadmap, high-cost guardian/formal review, semantic review, review record, controlled merge, release, npm, tag, GitHub Release, live config mutation, or shared contract/schema/failure vocabulary changes.
- Current Lane: round-9-wi-4-idle-read-surfaces

## Runtime Evidence

- Run Entry: Scheduler thread `019ebecb-4123-7600-9527-6616c5e94d84` consumed worker recovery result, merged latest `origin/main` closeout carrier facts into PR #1473 branch, and is preparing exact-head review artifacts for WI-1232.
- Logs Entry: Worksite `/Users/mc/.codex/worktrees/c98a/Loom` on branch `work/1232-idle-read-surfaces`; branch is reconciled with current `origin/main`; correction scope is limited to WI-1232 review/gate readiness after #1234 closeout landed on main.
- Diagnostics Entry: Non-review and review blockers are clear locally; scheduler is consuming merge gate evidence for PR #1473.
- Verification Entry: Current validation evidence: fact-chain, state-check, suite validate/evidence/carrier validate, PR metadata readback, scheduler-authored spec/implementation review records, and local PR gate review consumption.
- Lane Entry: round-9-wi-4-idle-read-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1232.md
- Dynamic Truth: .loom/progress/WI-1232.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
