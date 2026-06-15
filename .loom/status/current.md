# Current Status

## Derived Fact Chain View

- Item ID: WI-1245
- Goal: Update README, adoption docs, CLI help, and downstream migration guidance for runtime provider modes.
- Scope: Issue #1245 / PR #1472 only: document repo-local-wrapper and global-cli runtime provider modes, second-machine setup, validation commands, .loom/bin expectations, CLI help wording, command matrix guidance, and owned WI-1245 carrier/review/shadow/PR metadata alignment. Ownership constraints are limited to WI-1245 / PR #1472 docs/help changes, `.loom/work-items/WI-1245.md`, `.loom/progress/WI-1245*.json`, `.loom/progress/WI-1245.md`, `.loom/status/current.md`, `.loom/reviews/WI-1245*.json`, `.loom/specs/WI-1245/*`, `.loom/shadow/*-loom.json` surfaces consumed by this PR, and PR #1472 body metadata. Do not publish release artifacts, perform HotCP-specific PR edits, start #1246, run high-cost gates, merge, release, tag, publish, or change shared contract/schema/vocabulary.
- Execution Path: issue #1245 -> branch work/1245-runtime-provider-modes -> PR #1472 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1245.md
- Review Entry: .loom/reviews/WI-1245.json
- Validation Entry: python3 tools/loom.py help --json; python3 -m py_compile tools/loom.py; rg -n "repo-local-wrapper|global-cli|\.loom/bin|workstation" README.md README.zh-CN.md docs/adoption/README.md docs/adoption/installation-taxonomy.md docs/adoption/loom-installed-state-v2.md docs/adoption/unified-install-experience.md docs/adoption/external-runtime-companion-contract.md docs/methodology/harness/cli-command-matrix.md tools/loom.py; python3 tools/check_cli_contract.py; node bin/loom.mjs --help; git diff --check; PR metadata preflight/readback; fact-chain/state-check/shadow parity; scheduler-owned current-head review and later PR gate
- Closing Condition: PR #1472 for WI-1245 is refreshed to the current main head, PR metadata and repo carriers bind the current PR head/base, current-head review is recorded, scheduler-owned gates pass, and no_release closeout is consumed before #1246 starts.
- Current Checkpoint: merge
- Current Stop: WI-1245/#1245 terminal closeout facts have been consumed: PR #1472 merged by controlled merge at 2026-06-15T07:48:26Z as ed0e7080c0f463874faf486968557746167aa935 on origin/main; issue #1245 closed/completed at 2026-06-15T07:56:59Z; stale native blocked-by edges from #1243 and #1244 were removed and read back as blockedBy.nodes=[]; no_release applies for this docs/help and carrier-alignment scope.
- Next Step: none for WI-1245. #1246 remains open as the separate release and downstream migration closeout Work Item.
- Blockers: none
- Latest Validation Summary: Post-merge closeout evidence on 2026-06-15: PR #1472 is MERGED at 2026-06-15T07:48:26Z with merge commit ed0e7080c0f463874faf486968557746167aa935; origin/main after fetch is ed0e7080c0f463874faf486968557746167aa935 and contains the merge commit; issue #1245 is CLOSED/COMPLETED at 2026-06-15T07:56:59Z; GitHub native blockedBy for #1245 was reconciled from #1243/#1244 to totalCount=0; #1246 remains OPEN as the separate release/downstream migration closeout item; no_release remains final for WI-1245: no VERSION/tag/GitHub Release/npm publish/live action, package publication, workflow release execution, or shared contract/schema/parser vocabulary change occurred. Pre-merge retained validation includes merge-ready pass, hosted loom-pr-merge-gate rerun success, required checks success, PR body metadata readback, semantic review disposition pass with carrier-only head binding, fact-chain/state-check/shadow parity, suite not_applicable validation, and controlled-merge check/execute pass.
- Recovery Boundary: Terminal; WI-1245 docs/help and carrier-alignment work is merged and closed out. Do not start #1246, release/tag/publish, change shared contract/schema/vocabulary, or reopen this Work Item except for explicit terminal evidence correction.
- Current Lane: shared_fact_chain_status_lane,current_item_review_lane,shadow_carrier_lane

## Runtime Evidence

- Run Entry: Codex thread `019ec9cf-c7fb-7b73-a6f3-3db100aecded` resumed WI-1245/PR #1472 alignment on 2026-06-15T05:50:47Z.
- Logs Entry: Formal worksite `/Users/mc/.codex/worktrees/a9fc/Loom`; branch `work/1245-runtime-provider-modes`; pre-carrier-refresh head ac1de9aadc2a5f34c7c683e67b3272aeaf0db329; base `origin/main` 4e607c90bd8adddf6cd3106ad85af3d8d769f524.
- Diagnostics Entry: `/Users/mc/dev/Loom` main was read only as a non-authoritative locator and rejected as the execution site because it was on `main` and lacked WI-1245 carriers; `/Users/mc/.codex/worktrees/a9fc/Loom` is the registered branch worktree for PR #1472.
- Verification Entry: Low-cost recovery checks passed before carrier commit: `python3 .loom/bin/loom_init.py fact-chain --target .`; `python3 .loom/bin/loom_flow.py state-check --target . --item WI-1245`; `python3 .loom/bin/loom_flow.py flow resume --target . --item WI-1245`. `python3 .loom/bin/loom_flow.py flow build --target . --item WI-1245` returned block for missing formal suite/build evidence, classified as requiring a not_applicable suite path decision rather than fake spec/plan artifacts.
- Lane Entry: shared_fact_chain_status_lane,current_item_review_lane,shadow_carrier_lane

## Sources

- Static Truth: .loom/work-items/WI-1245.md
- Dynamic Truth: .loom/progress/WI-1245.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
