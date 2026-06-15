# Current Status

## Derived Fact Chain View

- Item ID: WI-1245
- Goal: Update README, adoption docs, CLI help, and downstream migration guidance for runtime provider modes.
- Scope: Issue #1245 / PR #1472 only: document repo-local-wrapper and global-cli runtime provider modes, second-machine setup, validation commands, .loom/bin expectations, CLI help wording, and command matrix guidance. Do not publish release artifacts, perform HotCP-specific PR edits, start #1246, run high-cost gates, merge, release, tag, publish, or change shared contract/schema/vocabulary.
- Execution Path: issue #1245 -> branch work/1245-runtime-provider-modes -> PR #1472 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1245.md
- Review Entry: .loom/reviews/WI-1245.json
- Validation Entry: python3 tools/loom.py help --json; python3 -m py_compile tools/loom.py; rg -n "repo-local-wrapper|global-cli|\.loom/bin|workstation" README.md README.zh-CN.md docs/adoption/README.md docs/adoption/installation-taxonomy.md docs/adoption/loom-installed-state-v2.md docs/adoption/unified-install-experience.md docs/adoption/external-runtime-companion-contract.md docs/methodology/harness/cli-command-matrix.md tools/loom.py; python3 tools/check_cli_contract.py; node bin/loom.mjs --help; git diff --check; PR metadata preflight/readback; fact-chain/state-check/shadow parity; scheduler-owned current-head review and later PR gate
- Closing Condition: PR #1472 for WI-1245 is refreshed to the current main head, PR metadata and repo carriers bind the current PR head/base, current-head review is recorded, scheduler-owned gates pass, and no_release closeout is consumed before #1246 starts.
- Current Checkpoint: build
- Current Stop: Round 10 recovery readback located the formal workspace at `/Users/mc/.codex/worktrees/a9fc/Loom`; PR #1472 and `origin/work/1245-runtime-provider-modes` both point at head ac1de9aadc2a5f34c7c683e67b3272aeaf0db329 with base 4e607c90bd8adddf6cd3106ad85af3d8d769f524, while the PR body metadata still referenced the old head 706aa65810b403ba1875f74f45368e15db4edc68.
- Next Step: Commit the WI-1245 carrier/status/suite-decision refresh, then immediately refresh PR body metadata and review evidence to the resulting branch head, push, read back GitHub PR/branch/checks, and stop before high-cost gate or merge scheduling.
- Blockers: High-cost gate, controlled merge, release/tag/publish, #1246, and any contract/schema/vocabulary change are blocked until separately granted. PR remains draft until scheduler-owned gate sequence is authorized.
- Latest Validation Summary: 2026-06-15T05:50:47Z readback: `git status --short --branch` in the formal worktree showed branch `work/1245-runtime-provider-modes` with WI-1245 carrier edits only; `git rev-parse HEAD` and `git rev-parse origin/work/1245-runtime-provider-modes` both returned ac1de9aadc2a5f34c7c683e67b3272aeaf0db329; `git rev-parse origin/main` returned 4e607c90bd8adddf6cd3106ad85af3d8d769f524; `gh pr view 1472 --json ...` returned PR head ac1de9aadc2a5f34c7c683e67b3272aeaf0db329/base 4e607c90bd8adddf6cd3106ad85af3d8d769f524 and stale body metadata at head 706aa65810b403ba1875f74f45368e15db4edc68/base a1712a017d597b22a9bf08ca5fd991d78127acf8; `python3 .loom/bin/loom_init.py fact-chain --target .` passed; `python3 .loom/bin/loom_flow.py state-check --target . --item WI-1245` passed; `python3 .loom/bin/loom_flow.py flow build --target . --item WI-1245` classified the remaining gap as missing suite path/build evidence, so this carrier refresh adds the official not_applicable suite path decision instead of fake formal suite artifacts.
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
