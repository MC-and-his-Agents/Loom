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
- Current Checkpoint: merge
- Current Stop: PR #1461 readiness carriers are being advanced from build to merge checkpoint for head 82b06c38f0cdc06bd594543807b7e4c80b21e1a2 after shadow parity, PR metadata, and draft-to-ready transition were validated locally.
- Next Step: Refresh the WI-1244 review record and the two granted shadow files for the updated status surface, commit/push the carrier update, update PR #1461 head metadata, rerun local/hosted PR readiness gates, then send lane_release/lane_blocked_update or request merge_lane; do not merge without merge_lane grant.
- Blockers: None
- Latest Validation Summary: 2026-06-12 PR-readiness validation for PR #1461 head 82b06c38f0cdc06bd594543807b7e4c80b21e1a2 passed local shadow/status/root checks: python3 -m json.tool .loom/shadow/merge-ready-loom.json and .loom/shadow/closeout-loom.json; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1244 --dry-run; git diff --check; python3 .loom/bin/loom_init.py verify --target .; governance-profile status; runtime-parity validate; adopt verify --item WI-1244; python3 tools/loom.py pr metadata-preflight 1461 --head-sha 82b06c38f0cdc06bd594543807b7e4c80b21e1a2 --work-item WI-1244 --surface merge_ready --json. After #1461 was marked ready for review, local pr-gate consumed PR metadata and authored review with no missing_inputs; the only remaining local readiness transition was this recovery writeback from build to merge checkpoint, followed by review/shadow refresh and final pr-gate rerun.
- Recovery Boundary: WI-1244/#1244 PR #1461 readiness only under watcher-lane-grant-R10-WI-1244-pr-readiness-202606121222 and watcher-shadow-lane-grant-R10-WI-1244-pr-readiness-202606121301. May write WI-1244 fact-chain/status/review carriers and only .loom/shadow/merge-ready-loom.json plus .loom/shadow/closeout-loom.json for readiness. Do not merge #1461, run controlled merge, perform post-merge closeout sync, release/npm/live/VERSION/tag/GitHub Release/npm publish, process #1245/#1246/#1238 closeout, edit PR #1463/WI-1263, or change shared contract/schema/parser/failure vocabulary.
- Current Lane: shared_fact_chain_status_lane,current_item_review_lane,high_cost_gate_lane,shadow_carrier_lane

## Runtime Evidence

- Run Entry: Scheduler consumed watcher lane grant watcher-lane-grant-R10-WI-1244-pr-readiness-202606121222 after Round 8 WI-1263 terminal release was accepted.
- Logs Entry: Scheduler thread 019ebb62-095b-7a23-a269-2906cce8e742 owns WI-1244 PR #1461 readiness refresh, current status/progress, current-head review, allowed high-cost gate classification, and lane_release/lane_blocked_update or later merge_lane request.
- Diagnostics Entry: WI-1244 exercises HotCP-style global CLI runtime repositories without `.loom/bin`, retained `.loom/bin` repo-local compatibility, installed-state/detect/doctor/verify/fact-chain/status surfaces, repair/upgrade planning, and provider mismatch diagnostics.
- Verification Entry: Local validation and current-head review passed on the rebased WI-1244 branch against origin/main `da4c1761d7c16f3ac7212638dae99af941178682`; review record `.loom/reviews/WI-1244.json` is approved for reviewed_head `dc228d55c2cec1ebc385c8beabc8be47c0bd72a3`. PR body, hosted checks, and PR readiness gates still need refresh before lane release or merge_lane request.
- Lane Entry: shared_fact_chain_status_lane,current_item_review_lane,high_cost_gate_lane

## Sources

- Static Truth: .loom/work-items/WI-1244.md
- Dynamic Truth: .loom/progress/WI-1244.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
