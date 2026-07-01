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
- Current Checkpoint: merge
- Current Stop: v0.26.0 release candidate metadata, npm/package/plugin payload metadata, release readiness evidence, and WI-1865 carriers are prepared on branch work/1865-v0.26.0-release.
- Next Step: Record release review, refresh carrier shadows, create the release PR, bind PR metadata to the current head, then run local and hosted gates before merging to main for publication.
- Blockers: None recorded.
- Latest Validation Summary: Pre-release validation passed: py_compile_clean for release tooling, version_surface_check, check_release_surface, check_npm_package aggregate with payload file count 388 and plugin payload hash c451654a83380621ed7af0ff2eafa461512a0cc8c67d6373f4429ffc5526c00e, npm pack dry-run entryCount 388, release-readback CLI contract in 1.93s, aggregate CLI contract in 350.93s, suite validate/evidence/carrier for WI-1865, fact-chain, and pre-publication release readback verdict missing as expected.
- Recovery Boundary: WI-1865 owns v0.26.0 root release authority, package/plugin payload metadata/hash, release readiness evidence, WI-1865 carriers, WI-1859 implementation-merged progress consumption, release PR metadata, publication readback, terminal carrier closeout, and #1859/#1860-#1865 plus milestone #23 closeout. It does not add new runtime behavior beyond merged #1859, does not publish legacy installer, does not change plugin surface compatibility, does not do multi-repo batching, and does not close issues before release readback plus terminal carrier closeout.
- Current Lane: release-pr

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1865 release work is active in `/Users/mc/dev/Loom.worktrees/1865-v0.26.0-release` on branch `work/1865-v0.26.0-release`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1865.md`.
- Diagnostics Entry: Branch starts from main at `06f85307587308121627bbf2f6603dc96f629721`, the merge commit for implementation PR #1866.
- Verification Entry: pre-release package, plugin payload, release surface, suite, fact-chain, npm dry-run, release-readback, and CLI contract checks passed before PR creation.
- Lane Entry: release-pr

## Sources

- Static Truth: .loom/work-items/WI-1865.md
- Dynamic Truth: .loom/progress/WI-1865.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
