# Current Status

## Derived Fact Chain View

- Item ID: WI-1778
- Goal: 执行 v0.21.0 closeout readback 主路径产品化能力的 release closeout。
- Scope: bump root Loom CLI release authority to `v0.21.0`, align root npm package and Codex plugin payload release metadata, add v0.21.0 release readiness evidence, publish tag/GitHub Release/npm after merge, and close out #1778/#1774/milestone #18 after release readback. Ownership is limited to v0.21.0 release authority, plugin payload release metadata/hash, release readiness evidence, WI-1778 carriers, and current status/shadow readback. Do not bump plugin surface version, skills registry version, skill contract versions, or legacy `@mc-and-his-agents/loom-installer`.
- Execution Path: issue #1778 -> branch work/1778-v021-release-closeout -> release readiness evidence -> release PR -> main push release workflow -> release readback -> #1778/#1774/milestone #18 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1778.md
- Review Entry: .loom/reviews/WI-1778.json
- Validation Entry: release readback, release/package checks, closeout/readback regressions, npm package smoke, suite/fact-chain, hosted checks, and post-merge release readback.
- Closing Condition: v0.21.0 tag, GitHub Release, npm `@mc-and-his-agents/loom@0.21.0`, plugin payload metadata/hash, #1778/#1774 closeout evidence, and milestone #18 readback are consistent.
- Current Checkpoint: merge
- Current Stop: v0.21.0 release closeout candidate is prepared on branch `work/1778-v021-release-closeout`: release authority, plugin payload metadata, release readiness evidence, and WI-1778 carriers are being validated before release PR review.
- Next Step: Run release/package/local Loom validation, open the release PR, consume hosted checks and controlled merge, then read back tag/GitHub Release/npm before terminal closeout.
- Blockers: none
- Latest Validation Summary: 2026-06-23 release candidate validation passed on branch `work/1778-v021-release-closeout`: git diff --check; python3 tools/version_surface_check.py; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; npm run test:package; npm pack --dry-run --json --ignore-scripts; python3 tools/check_cli_contract.py --surface release-readback; python3 tools/check_cli_contract.py --fixture-group ship-wrapper; python3 tools/loom.py suite validate/evidence/carrier --target . --item WI-1778 --json; python3 tools/loom.py fact-chain --target . --item WI-1778 --json; python3 tools/loom_flow.py state-check --target . --item WI-1778; python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking. Live release readback for v0.21.0 returned verdict `missing` with gaps `tag_missing`, `github_release_missing`, `npm_version_missing`, and `workflow_run_target_commit_missing`, confirming the publish path is still unoccupied while package surface is aligned.
- Recovery Boundary: WI-1778 owns v0.21.0 root release authority, plugin payload release metadata/hash, release readiness evidence, WI-1778 carriers, and current status/shadow readback. It does not add new closeout/readback product behavior beyond publishing the completed #1774 tree, does not publish a legacy installer version, and does not change plugin surface compatibility.
- Current Lane: release-closeout

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1778 release closeout started in repo-relative workspace `.` on branch `work/1778-v021-release-closeout`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1778.md`.
- Diagnostics Entry: `loom release readback` / `loom release resume` must classify v0.21.0 publication state as `published`, `missing`, `drifted`, or `blocked`.
- Verification Entry: Release/package checks, release-readback regression, ship-wrapper regression, npm smoke, npm pack dry-run, suite/fact-chain, PR metadata, hosted checks, controlled merge, and post-merge release readback are required before terminal closeout.
- Lane Entry: release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1778.md
- Dynamic Truth: .loom/progress/WI-1778.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
