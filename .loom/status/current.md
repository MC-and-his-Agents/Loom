# Current Status

## Derived Fact Chain View

- Item ID: WI-1855
- Goal: 发布 v0.25.0 readiness guidance release。
- Scope: bump root Loom CLI release authority to `v0.25.0`, align root npm package and Codex plugin payload release metadata/hash, add v0.25.0 release readiness evidence, publish tag/GitHub Release/npm after merge, and close out #1850/#1851-#1855 plus milestone #22 after release readback. Ownership is limited to v0.25.0 release authority, plugin payload release metadata/hash, release readiness evidence, WI-1855 carriers, and current status/shadow readback.
- Execution Path: issue #1855 -> branch work/1855-v0.25.0-release -> release readiness evidence -> release PR -> main push release workflow -> release readback -> #1850/#1851-#1855/milestone #22 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1855.md
- Review Entry: .loom/reviews/WI-1855.json
- Validation Entry: release readback, release/package checks, CLI contract checks, npm package dry-run, suite/fact-chain, hosted checks, and post-merge release readback.
- Closing Condition: v0.25.0 tag, GitHub Release, npm `@mc-and-his-agents/loom@0.25.0`, plugin payload metadata/hash, #1850/#1851-#1855 closeout evidence, and milestone #22 readback are consistent.
- Current Checkpoint: closed_out
- Current Stop: WI-1855 release closeout synced for v0.25.0: release PR #1857 merged at d9ca2ed4e281cf123fc92a435e335d2600374f4d; published release readback consumed into terminal repo carrier state.
- Next Step: None.
- Blockers: None recorded.
- Latest Validation Summary: Pre-release local validation passed on 2026-07-01; PR #1857 local PR gate, hosted checks, and merge check passed; release workflow `loom-cli-release` run 28512888728 published v0.25.0; final release readback for merge commit d9ca2ed4e281cf123fc92a435e335d2600374f4d passed with verdict `published`.
- Recovery Boundary: WI-1855 owns v0.25.0 root release authority, plugin payload release metadata/hash, release readiness evidence, WI-1855 carriers, WI-1851 implementation-merged progress consumption, and status/shadow readback. It does not add new runtime behavior beyond the merged #1851 implementation, does not publish a legacy installer version, and does not change plugin surface compatibility.
- Current Lane: release-closeout-sync

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1855 release work is active in `/Users/mc/dev/Loom.worktrees/1855-v0.25.0-release` on branch `work/1855-v0.25.0-release`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1855.md` and `docs/evidence/v0.25.0-release-readiness.md`.
- Diagnostics Entry: PR #1856 merged to main at `4cde91ccedaf0c8a11b38030d8452888c7e43d58`; release branch starts from that merge commit.
- Verification Entry: pre-release local validation passed; publication readback remains pending until the release PR merges and the main-push workflow publishes v0.25.0.
- Lane Entry: release-pr-gate

## Sources

- Static Truth: .loom/work-items/WI-1855.md
- Dynamic Truth: .loom/progress/WI-1855.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
