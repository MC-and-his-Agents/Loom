# Current Status

## Derived Fact Chain View

- Item ID: WI-1244
- Goal: Add regression fixtures for HotCP-style repositories that use the global Loom CLI runtime without .loom/bin while preserving retained .loom/bin compatibility behavior.
- Scope: Issue #1244 / WI-6 only: synthetic regression fixtures and CLI contract validation for no-.loom/bin global CLI runtime, repo-local .loom/bin compatibility runtime, retained .loom/bin repair/upgrade planning, installed-state/detect/doctor/verify/fact-chain/status surfaces, and provider mismatch diagnostics. Do not process #1245/#1246/#1238 closeout, shadow carriers, controlled merge, release/npm/live actions, or shared contract/schema/parser/failure vocabulary changes.
- Execution Path: issue #1244 -> branch work/1244-global-cli-runtime-fixtures -> PR #1461 -> scheduler-owned current-head review and high-cost PR readiness gate -> watcher merge_lane request if ready
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1244.md
- Review Entry: .loom/reviews/WI-1244.json
- Validation Entry: python3 tools/py_compile_clean.py tools/check_cli_contract.py tools/loom.py tools/governance_surface.py; python3 tools/check_cli_contract.py --surface aggregate; python3 -m json.tool docs/evidence/fixtures/legacy-migration-validation-fixtures.json >/dev/null; python3 tools/loom.py suite inspect --target . --item WI-1244 --json; python3 tools/loom.py suite validate --target . --item WI-1244 --json; git diff --check origin/main...HEAD; python3 tools/loom.py pr metadata-preflight 1461 --head-sha <current-head> --work-item WI-1244 --surface merge_ready --json; python3 .loom/bin/loom_flow.py review read --target . --item WI-1244; python3 .loom/bin/loom_flow.py pr-gate check --target . --item WI-1244 --pr 1461 --head-sha <current-head>
- Closing Condition: PR #1461 for work/1244-global-cli-runtime-fixtures is refreshed onto current main, metadata/readback/review/high-cost PR readiness gates pass for current head, watcher grants merge_lane separately if merge-ready, and #1244 closeout is consumed without shadow/merge/closeout/release/scope expansion in this grant.
- Current Checkpoint: closed_out
- Current Stop: WI-1244/#1244 closeout-only carrier sync consumes the controlled merge of PR #1461 at 2026-06-12T13:29:24Z with merge commit 589ed8e54829faa366e3368897cd32b156d94c6a, records #1243 CLOSED/COMPLETED dependency reconciliation readback, and preserves no_release evidence. Issue #1244 remains open until this closeout PR is merged and host reconciliation is separately consumed.
- Next Step: Open and gate the narrow WI-1244 terminal carrier PR from origin/main 589ed8e54829faa366e3368897cd32b156d94c6a; request merge_lane only after exact closeout PR head/base/body/checks are clean. After that closeout PR lands, consume host reconciliation for #1244 and the stale #1243 dependency edge under a separate authorized step.
- Blockers: None for closeout-only PR preparation; final #1244 closeout remains pending closeout PR merge_lane plus post-merge host reconciliation/issue closure.
- Latest Validation Summary: Post-merge closeout readback prepared on 2026-06-12: PR #1461 is MERGED at 2026-06-12T13:29:24Z with merge commit 589ed8e54829faa366e3368897cd32b156d94c6a; origin/main is 589ed8e54829faa366e3368897cd32b156d94c6a; issue #1244 is still OPEN; predecessor #1243 is CLOSED/COMPLETED at 2026-06-11T11:09:41Z and no longer an active blocker; implementation evidence remains PR #1461 head 8d4d78e537601bea7d72a596f4804ee53f9c5d9e with hosted checks green before merge. This carrier-only closeout branch records terminal metadata, no_release, review/shadow/status refresh, and does not change implementation behavior.
- Recovery Boundary: WI-1244/#1244 terminal carrier sync only under watcher-closeout-pr-authorization-R10-WI-1244-202606121336. May update only WI-1244 closeout/status/progress/review/shadow/bootstrap/work-item carriers required for the closeout PR. Do not implement new behavior, process #1245/#1246/#1238, Round 8/9/11, Deferred roadmap, #1255, release/npm/live/VERSION/tag/GitHub Release/npm publish, shared contract/schema/parser/failure vocabulary changes, host issue closure, or any merge without separate watcher authorization.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: Scheduler consumed watcher closeout PR authorization watcher-closeout-pr-authorization-R10-WI-1244-202606121336 after PR #1461 merged and direct-main closeout was denied.
- Logs Entry: Scheduler thread 019ebb62-095b-7a23-a269-2906cce8e742 owns the WI-1244 closeout-only branch/PR preparation, terminal status/progress/review/shadow evidence, local closeout/pr-gate validation, and lane_release/lane_blocked_update or later merge_lane request.
- Diagnostics Entry: WI-1244 exercises HotCP-style global CLI runtime repositories without `.loom/bin`, retained `.loom/bin` repo-local compatibility, installed-state/detect/doctor/verify/fact-chain/status surfaces, repair/upgrade planning, and provider mismatch diagnostics.
- Verification Entry: Post-merge readback proved PR #1461 merged at 2026-06-12T13:29:24Z with merge commit `589ed8e54829faa366e3368897cd32b156d94c6a`, origin/main points to that merge commit, #1243 is closed/completed, #1244 remains open pending closeout PR merge and host reconciliation, and no_release/no publish or live action applies. Terminal closeout updates status/progress/review/shadow carriers only.
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1244.md
- Dynamic Truth: .loom/progress/WI-1244.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
