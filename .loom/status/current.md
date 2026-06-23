# Current Status

## Derived Fact Chain View

- Item ID: WI-1743
- Goal: 执行 v0.20.0 ship 主路径低摩擦交付能力的 release closeout。
- Scope: bump root Loom CLI release authority to `v0.20.0`, align root npm package and Codex plugin payload release metadata, retain v0.20.0 release readiness evidence, serially consume the completed WI-1742 terminal carrier in `.loom/progress/WI-1742.md`, publish tag/GitHub Release/npm after merge, and close out #1743/#1734/milestone #17 after release readback. Ownership constraints are limited to v0.20.0 release authority, plugin payload release metadata/hash, release readiness evidence, WI-1743 carriers, and WI-1742 terminal closeout readback. Do not bump plugin surface version, skills registry version, skill contract versions, or legacy `@mc-and-his-agents/loom-installer`.
- Execution Path: issue #1743 -> branch work/1743-v0.20-release -> release readiness evidence -> release PR -> main push release workflow -> release readback -> #1743/#1734/milestone #17 closeout.
- Workspace Entry: ././
- Recovery Entry: .loom/progress/WI-1743.md
- Review Entry: .loom/reviews/WI-1743.json
- Validation Entry: release readback, release/package checks, ship-wrapper regression, npm package smoke, suite/fact-chain, hosted checks, and post-merge release readback.
- Closing Condition: v0.20.0 tag, GitHub Release, npm `@mc-and-his-agents/loom@0.20.0`, plugin payload metadata/hash, #1743/#1734 closeout evidence, and milestone #17 readback are consistent.
- Current Checkpoint: merge
- Current Stop: v0.20.0 release candidate files, WI-1743 minimal suite, release readback, package/release checks, npm package smoke, npm pack dry-run, and ship-wrapper regression passed locally; review, PR metadata, hosted checks, controlled merge, and post-merge release readback remain.
- Next Step: Run suite/fact-chain/state-check readback, shadow parity, review, PR metadata, hosted checks, controlled merge, and post-merge release readback.
- Blockers: none
- Latest Validation Summary: 2026-06-23 local release/package validation passed on branch `work/1743-v0.20-release`: release readback classified v0.20.0 as unpublished/unoccupied with npm latest `0.19.0`; `stamp_plugin_payload_metadata.py --source-git-sha unreleased --json`, `version_surface_check.py`, `check_npm_package.py --surface plugin-payload-hash`, `check_release_surface.py`, `check_npm_package.py`, `npm run test:package`, `npm pack --dry-run --json --ignore-scripts`, `tools/check_cli_contract.py --fixture-group ship-wrapper`, and `git diff --check` passed. `state-check` initially blocked only on non-canonical pending evidence freshness and was repaired to canonical `current` / `present` values before rerun.
- Recovery Boundary: WI-1743 owns v0.20.0 root release authority, plugin payload release metadata/hash, release readiness evidence, and WI-1743 carriers. It does not publish a legacy installer version, change plugin surface compatibility version, or alter #1711-#1722/v0.19.0 state.
- Current Lane: release-closeout

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1743 release lane started in issue-scoped worktree `/Users/mc/dev/Loom-WI-1743-v0.20-release` on branch `work/1743-v0.20-release`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1743.md`.
- Diagnostics Entry: v0.20.0 release candidate publishes the completed ship main-path capability and keeps release/versioned closeout as explicit upgrade paths.
- Verification Entry: Release readback, package/release checks, ship-wrapper regression, suite/fact-chain/state-check, PR metadata, hosted checks, controlled merge, and post-merge release readback are consumed before final closeout.
- Lane Entry: release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1743.md
- Dynamic Truth: .loom/progress/WI-1743.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
