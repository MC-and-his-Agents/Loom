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
- Current Checkpoint: build
- Current Stop: WI-1245 carrier/build evidence, spec-review, and implementation review are recorded; implementation review includes `semantic_review_disposition: passed` and only carrier-only drift remains after the reviewed head.
- Next Step: Push branch `work/1245-runtime-provider-modes`, refresh PR #1472 body metadata to the pushed head, read back GitHub PR/head/checks, and stop before high-cost gate or merge scheduling.
- Blockers: none
- Latest Validation Summary: 2026-06-15T07:41Z WI-1245 current-head carrier validation on branch work/1245-runtime-provider-modes head 62640009409a0db828246bdc5ef96a30d20d1889: python3 tools/skills_surface.py check passed; python3 tools/loom_check.py --profile source --source-surface contract-only passed; python3 .loom/bin/loom_flow.py flow build --target . --item WI-1245 --build-evidence .loom/progress/WI-1245-build-evidence.json passed with integrated execution evidence; prior current-head validation retained as input: python3 tools/loom.py help --json passed; python3 -m py_compile tools/loom.py passed; rg provider-mode coverage passed across README, adoption docs, CLI matrix, and tools/loom.py; node bin/loom.mjs --help passed; git diff --check passed; python3 .loom/bin/loom_init.py fact-chain --target . passed; python3 .loom/bin/loom_flow.py state-check --target . --item WI-1245 passed; python3 tools/loom.py suite inspect --target . --item WI-1245 --json passed; python3 tools/loom.py suite validate --target . --item WI-1245 --json returned result=not_applicable with blocking_gaps=[]; python3 tools/loom.py suite carrier validate --target . --item WI-1245 --json passed; python3 .loom/bin/loom_flow.py shadow-parity --target . passed; python3 tools/check_cli_contract.py passed all 6 surfaces in 377.03s; PR #1472 readback returned head 62640009409a0db828246bdc5ef96a30d20d1889/base 4e607c90bd8adddf6cd3106ad85af3d8d769f524; PR metadata preflight for review and merge_ready passed before and after gh pr edit readback with matching machine block.
- Recovery Boundary: WI-1245 / PR #1472 carrier, PR metadata, review, and shadow recovery only. Do not run or consume high-cost gate/guardian/loom-pr-merge-gate success, do not controlled merge, do not release/tag/publish, do not start #1246, do not read retired/systemError thread turns, and do not change shared contract/schema/vocabulary.
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
