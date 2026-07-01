# Current Status

## Derived Fact Chain View

- Item ID: WI-1874
- Goal: 发布 v0.26.1 closeout 恢复打磨。
- Scope: bump root Loom CLI release authority to v0.26.1, align npm package and Codex plugin payload release metadata/hash, add v0.26.1 release readiness evidence, prepare and merge the release PR, then read back GitHub Release/npm/tag/workflow and close out #1869/#1874 plus milestone #24 after terminal carrier closeout.
- Execution Path: issue #1874 -> branch work/1874-v0.26.1-release -> release readiness evidence -> release PR -> main push release workflow -> release readback -> #1869/#1874/milestone #24 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1874.md
- Review Entry: .loom/reviews/WI-1874.json
- Validation Entry: release readback, release/package checks, CLI contract checks, npm package dry-run, suite/fact-chain, hosted checks, and post-merge release readback.
- Closing Condition: v0.26.1 tag, GitHub Release, npm @mc-and-his-agents/loom@0.26.1, plugin payload metadata/hash, #1869/#1874 closeout evidence, and milestone #24 readback are consistent.
- Current Checkpoint: closed_out
- Current Stop: WI-1874 release closeout synced for v0.26.1: release PR #1877 merged at 37d78b64c8d60e227be38a814792df6cac0b8fa8; published release readback consumed into terminal repo carrier state.
- Next Step: None.
- Blockers: None recorded.
- Latest Validation Summary: local pre-release validation passed on 2026-07-01 for `python3 tools/version_surface_check.py`, `python3 tools/check_release_surface.py`, `python3 tools/check_npm_package.py --surface aggregate`, `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/stamp_plugin_payload_metadata.py tools/version_surface_check.py`, `npm pack --dry-run --json --ignore-scripts`, `python3 tools/check_cli_contract.py --surface release-readback`, `python3 tools/check_cli_contract.py --surface aggregate`, `python3 tools/loom.py suite validate --target . --item WI-1874 --json`, `python3 tools/loom.py suite evidence validate --target . --item WI-1874 --json`, `python3 tools/loom.py suite carrier validate --target . --item WI-1874 --json`, `python3 .loom/bin/loom_init.py fact-chain --target .`, `python3 tools/loom.py skills release-check --json`, `python3 tools/check_demo_bootstrap_fixture.py`, and `git diff --check`; release readback verdict is `missing` with only expected pre-publication gaps.
- Recovery Boundary: WI-1874 owns v0.26.1 root release authority, package/plugin payload metadata/hash, release readiness evidence, release PR metadata, publication readback, terminal carrier closeout, and #1869/#1874 plus milestone #24 closeout. It does not add new runtime behavior beyond merged PR #1875, does not publish legacy installer, does not change plugin surface compatibility, and does not close issues before release readback plus terminal carrier closeout.
- Current Lane: release-closeout-sync

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1874 release work is active in `/Users/mc/dev/Loom.worktrees/1874-v0.26.1-release` on branch `work/1874-v0.26.1-release`.
- Logs Entry: Validation output is retained in this Codex thread and will be summarized in `.loom/progress/WI-1874.md`.
- Diagnostics Entry: Branch starts from main after #1875 merged and targets #1874 v0.26.1 release only.
- Verification Entry: release/package/suite/fact-chain/aggregate/skills/demo/diff validation passed locally before release review.
- Lane Entry: release

## Sources

- Static Truth: .loom/work-items/WI-1874.md
- Dynamic Truth: .loom/progress/WI-1874.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
