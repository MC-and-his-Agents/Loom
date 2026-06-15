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
- Current Checkpoint: closed_out
- Current Stop: PR #1497 merged into `main` as `0204c3e0360d81bc95247d960ee4755116d85e47`; push-to-main `loom-cli-release` run `27559414536` succeeded; `v0.14.0` is visible in Git tag, GitHub Release, npm package, installed/global CLI readback, and no-`.loom/bin` global-cli fixture evidence; #1246 is `CLOSED` / `COMPLETED`.
- Next Step: Close parent FR #1238 after this repo carrier closeout sync records the terminal release evidence.
- Blockers: none
- Latest Validation Summary: 2026-06-15T16:38Z post-merge WI-1246 release readback: PR #1497 is `MERGED` with head `6338166f8f23c4c7a201e17acab1b44953b12fd1` and merge commit `0204c3e0360d81bc95247d960ee4755116d85e47`; push-to-main `loom-cli-release` run `27559414536` completed successfully for head `0204c3e0360d81bc95247d960ee4755116d85e47`; `refs/tags/v0.14.0` dereferences to the merge commit; GitHub Release `v0.14.0` is published as `Loom CLI v0.14.0`; `npm view @mc-and-his-agents/loom@0.14.0 version dist.tarball dist.integrity time --json` returned version `0.14.0`; global npm install readback shows `@mc-and-his-agents/loom@0.14.0`; `/opt/homebrew/bin/loom version --json` returned `repo_version=v0.14.0`; `python3 tools/check_release_surface.py --surface installed-global-cli-smoke --show-surface-evidence` passed; a temporary no-`.loom/bin` global-cli fixture using the installed global `loom` command passed `installed-state validate`, `detect`, `doctor`, `verify`, `fact-chain`, and `story`, with `status` confirming the global `loom status` entrypoint while blocking only on synthetic fixture governance carriers outside the runtime provider contract; #1246 readback is `CLOSED` / `COMPLETED`.
- Recovery Boundary: Keep scope limited to release closeout version authority, evidence carriers, PR metadata, and #1246/#1238 closeout records. Do not change unrelated runtime behavior, schemas, parsers, failure vocabulary, Round 9, Round 11, deferred #1318, or downstream repositories.
- Current Lane: release_closeout_lane,version_authority_lane,current_item_review_lane,shadow_carrier_lane

## Runtime Evidence

- Run Entry: Codex thread active goal for #1246 release/downstream migration closeout resumed on 2026-06-15; repository carriers use portable workspace entry `.` for CI and PR-gate consumption.
- Logs Entry: Branch `work/1246-release-closeout`; base `origin/main` `52a553f214f9b8104852dc5d29fedae0754dcb8e`; selected release candidate `v0.14.0` / npm `0.14.0`.
- Diagnostics Entry: `/Users/mc/dev/Loom` main was read only for release fact table and had stale WI-1245 terminal carriers; release writes are confined to the registered issue-scoped worktree.
- Verification Entry: Local release/version/package/CLI/skills validation passed for `v0.14.0` on branch `work/1246-release-closeout`; release evidence locator is `docs/evidence/v0.14.0-release-readiness.md`; WI-1245 stale active workspace carrier was terminalized to `closed_out` using GitHub readback for already-closed #1245. Post-merge live release evidence is complete for PR #1497, release run `27559414536`, Git tag `v0.14.0`, GitHub Release `v0.14.0`, npm `@mc-and-his-agents/loom@0.14.0`, installed/global CLI smoke, and no-`.loom/bin` global-cli fixture runtime/provider validation.
- Lane Entry: release_closeout_lane,version_authority_lane,current_item_review_lane,shadow_carrier_lane

## Sources

- Static Truth: .loom/work-items/WI-1246.md
- Dynamic Truth: .loom/progress/WI-1246.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
