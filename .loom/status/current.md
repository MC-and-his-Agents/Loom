# Current Status

## Derived Fact Chain View

- Item ID: WI-1865
- Goal: 发布 v0.26.0 runtime-upgrade 安全 lane。
- Scope: bump root Loom CLI release authority to v0.26.0, align npm package and Codex plugin payload release metadata/hash, add v0.26.0 release readiness evidence, prepare and merge release PR, then read back GitHub Release/npm/tag/workflow and close out #1859/#1860-#1865 plus milestone #23 after terminal carrier closeout.
- Execution Path: issue #1865 -> branch work/1865-v0.26.0-release -> release readiness evidence -> release PR -> main push release workflow -> release readback -> #1859/#1860-#1865/milestone #23 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1865.md
- Review Entry: .loom/reviews/WI-1865.json
- Validation Entry: release readback, release/package checks, CLI contract checks, npm package dry-run, suite/fact-chain, hosted checks, and post-merge release readback.
- Closing Condition: v0.26.0 tag, GitHub Release, npm @mc-and-his-agents/loom@0.26.0, plugin payload metadata/hash, #1859/#1860-#1865 closeout evidence, and milestone #23 readback are consistent.
- Current Checkpoint: closed_out
- Current Stop: WI-1865 release closeout synced for v0.26.0: release PR #1867 merged at d892586713de176144a908166c8b7a512c2421af; published release readback consumed into terminal repo carrier state.
- Next Step: Commit and merge the carrier-only closeout PR, then close #1859/#1860-#1865 and milestone #23 after post-merge readback confirms terminal carrier on main.
- Blockers: None recorded.
- Latest Validation Summary: v0.26.0 release validation passed: release PR #1867 merged at d892586713de176144a908166c8b7a512c2421af; release workflow run 28524645818 succeeded; tag v0.26.0 resolves to d892586713de176144a908166c8b7a512c2421af; GitHub Release https://github.com/MC-and-his-Agents/Loom/releases/tag/v0.26.0 is published; npm @mc-and-his-agents/loom@0.26.0 exists with latest=0.26.0; release readback verdict is published; carrier closeout-sync wrote terminal state closed_out.
- Recovery Boundary: WI-1865 owns v0.26.0 root release authority, package/plugin payload metadata/hash, release readiness evidence, WI-1865 carriers, WI-1859 implementation-merged progress consumption, release PR metadata, publication readback, terminal carrier closeout, and #1859/#1860-#1865 plus milestone #23 closeout. It does not add new runtime behavior beyond merged #1859, does not publish legacy installer, does not change plugin surface compatibility, does not do multi-repo batching, and does not close issues before release readback plus terminal carrier closeout.
- Current Lane: release-closeout-sync

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1865 closeout work is active in `/Users/mc/dev/Loom.worktrees/1865-v0.26.0-release` on branch `work/1865-v0.26.0-closeout`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1865.md`.
- Diagnostics Entry: Branch starts from main at `d892586713de176144a908166c8b7a512c2421af`, the merge commit for release PR #1867.
- Verification Entry: post-publish release readback is `published`; tag, GitHub Release, npm latest, release workflow, package surface, and terminal carrier are consistent.
- Lane Entry: release-closeout-sync

## Sources

- Static Truth: .loom/work-items/WI-1865.md
- Dynamic Truth: .loom/progress/WI-1865.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
