# Current Status

## Derived Fact Chain View

- Item ID: WI-1246
- Goal: Release Loom CLI global-cli runtime provider support and record downstream migration closeout evidence for #1246 before closing parent FR #1238.
- Scope: Issue #1246 only: bump Loom CLI release authority from `v0.13.10` to an unpublished `v0.14.0`; validate release/version/package/CLI/skills surfaces; create and merge the release closeout PR; consume post-merge `loom-cli-release` push run, Git tag, GitHub Release, npm package, installed/global CLI smoke, and no-`.loom/bin` global-cli fixture evidence; close #1246 then #1238 in child-to-parent order. Ownership constraints are limited to `VERSION`, `package.json`, `skills/loom-adopt`, `skills/loom-build`, `skills/loom-handoff`, `skills/loom-init`, `skills/loom-merge-ready`, `skills/loom-pre-review`, `skills/loom-resume`, `skills/loom-retire`, `skills/loom-review`, `skills/loom-spec-review`, `skills/loom-story`, `.loom/bootstrap/init-result.json`, `.loom/work-items/WI-1246.md`, `.loom/progress/WI-1246.md`, `.loom/progress/WI-1246-build-evidence.json`, `.loom/reviews/WI-1246.json`, `.loom/specs/WI-1246`, `.loom/status/current.md`, `.loom/shadow/merge-ready-loom.json`, `.loom/shadow/closeout-loom.json`, `docs/evidence/v0.14.0-release-readiness.md`, PR body metadata, #1246/#1238 closeout records, and the minimal `.loom/progress/WI-1245.md` terminal checkpoint correction needed to remove stale active workspace drift after #1245 was already CLOSED/COMPLETED.
- Execution Path: issue #1246 -> branch work/1246-release-closeout -> release closeout PR -> controlled merge -> push-to-main release run -> live release readback -> #1246 closeout -> #1238 closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1246.md
- Review Entry: .loom/reviews/WI-1246.json
- Validation Entry: python3 tools/version_surface_check.py; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; npm run test:package; npm pack --dry-run --json --ignore-scripts; node bin/loom.mjs --help; node bin/loom.mjs version --json; python3 tools/skills_surface.py check; python3 tools/loom.py skills package --json; python3 tools/loom.py skills release-check --json; python3 tools/check_cli_contract.py; git diff --check; PR metadata preflight/readback; merge-ready gate; post-merge loom-cli-release run readback; Git tag/GitHub Release/npm/global CLI/fixture readback
- Closing Condition: `v0.14.0` is consistently visible in repo version files, Git tag, GitHub Release, npm package, installed/global CLI readback, and no-`.loom/bin` global-cli fixture evidence; #1246 and then #1238 are closed/completed with closeout evidence.
- Current Checkpoint: build
- Current Stop: Pre-release fact table was established, `v0.14.0` was selected as the lowest unoccupied minor release after `v0.13.10`, and repo/package/generated skill package version authority surfaces were updated on branch `work/1246-release-closeout`.
- Next Step: Commit the validated version/evidence/carrier update, write the current-head review record bound to that commit, create the release closeout PR, and bind PR metadata to the current head before merge-ready. Post-merge release evidence remains pending until the release PR is merged and the push-to-main `loom-cli-release` run completes.
- Blockers: none
- Latest Validation Summary: 2026-06-15T15:15Z WI-1246 local release validation on branch `work/1246-release-closeout`: pre-release occupancy confirmed current GitHub Release/npm/repo version at `v0.13.10` / `0.13.10` and candidate `v0.14.0` / `0.14.0` absent across fetched git tags, GitHub Release, and npm; `python3 tools/version_surface_check.py` passed; `python3 tools/check_release_surface.py` passed; `python3 tools/check_npm_package.py` passed for `@mc-and-his-agents/loom@0.14.0` with payload_file_count=2275; `npm run test:package` passed 4 tests; `npm pack --dry-run --json --ignore-scripts` passed for `@mc-and-his-agents/loom@0.14.0` with 2275 files; `node bin/loom.mjs --help` passed; `node bin/loom.mjs version --json` returned `repo_version=v0.14.0`; `python3 tools/skills_surface.py check` passed; `python3 tools/loom.py skills package --json` passed with all package `repo_version=v0.14.0`; `python3 tools/loom.py skills release-check --json` passed; `python3 tools/loom.py suite inspect --target . --item WI-1246 --json` passed; `python3 tools/loom.py suite validate --target . --item WI-1246 --json` returned `result=not_applicable` with `blocking_gaps=[]`; `python3 tools/loom.py suite carrier validate --target . --item WI-1246 --json` passed; `python3 tools/check_cli_contract.py` passed all 6 surfaces in 355.14s; `python3 tools/loom_check.py --profile source --source-surface contract-only .` passed; `git diff --check` passed; `python3 .loom/bin/loom_init.py fact-chain --target .` passed with workspace entry `.`; `python3 .loom/bin/loom_flow.py state-check --target . --item WI-1246` passed after minimal `.loom/progress/WI-1245.md` terminal checkpoint correction for already-closed #1245; `python3 .loom/bin/loom_flow.py flow build --target . --item WI-1246 --build-evidence .loom/progress/WI-1246-build-evidence.json` passed with attempt `WI-1246-build-a179440ede47-7deb5ac8c966`.
- Recovery Boundary: Keep scope limited to release closeout version authority, evidence carriers, PR metadata, and #1246/#1238 closeout records. Do not change unrelated runtime behavior, schemas, parsers, failure vocabulary, Round 9, Round 11, deferred #1318, or downstream repositories.
- Current Lane: release_closeout_lane,version_authority_lane,current_item_review_lane,shadow_carrier_lane

## Runtime Evidence

- Run Entry: Codex thread active goal for #1246 release/downstream migration closeout resumed on 2026-06-15; repository carriers use portable workspace entry `.` for CI and PR-gate consumption.
- Logs Entry: Branch `work/1246-release-closeout`; base `origin/main` `52a553f214f9b8104852dc5d29fedae0754dcb8e`; selected release candidate `v0.14.0` / npm `0.14.0`.
- Diagnostics Entry: `/Users/mc/dev/Loom` main was read only for release fact table and had stale WI-1245 terminal carriers; release writes are confined to the registered issue-scoped worktree.
- Verification Entry: Local release/version/package/CLI/skills validation passed for `v0.14.0` on branch `work/1246-release-closeout`; release evidence locator is `docs/evidence/v0.14.0-release-readiness.md`; WI-1245 stale active workspace carrier was terminalized to `closed_out` using GitHub readback for already-closed #1245. Post-merge live release evidence remains pending.
- Lane Entry: release_closeout_lane,version_authority_lane,current_item_review_lane,shadow_carrier_lane

## Sources

- Static Truth: .loom/work-items/WI-1246.md
- Dynamic Truth: .loom/progress/WI-1246.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
