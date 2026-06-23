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
- Current Checkpoint: closed_out
- Current Stop: v0.21.0 release closeout is complete: release PR #1788 merged, tag v0.21.0 points to the release merge commit, GitHub Release v0.21.0 is published, npm @mc-and-his-agents/loom@0.21.0 is published as latest, #1778 and parent #1774 are closed, and milestone #18 is closed with no open issue.
- Next Step: None. Merge this final carrier-only closeout PR, then read back main to confirm no release, issue, milestone, carrier, or shadow drift remains.
- Blockers: none
- Latest Validation Summary: 2026-06-23 post-merge release readback passed at release merge commit a1867d5744794a53bd994bbb9b31244accb871f0: `loom.py release readback --version v0.21.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --commit a1867d5744794a53bd994bbb9b31244accb871f0 --release-judgment release_required --json` found tag v0.21.0 pointing to the merge commit, GitHub Release v0.21.0 published at 2026-06-23T18:42:31Z, npm @mc-and-his-agents/loom@0.21.0 published with latest dist-tag 0.21.0, loom-cli-release run 28048511623 passed, #1778 and parent #1774 closed at 2026-06-23T18:44:56Z, and milestone #18 closed with open_issues=0.
- Recovery Boundary: WI-1778 owns v0.21.0 root release authority, plugin payload release metadata/hash, release readiness evidence, WI-1778 carriers, and current status/shadow readback. It does not add new closeout/readback product behavior beyond publishing the completed #1774 tree, does not publish a legacy installer version, and does not change plugin surface compatibility.
- Current Lane: release-closeout

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1778 release closeout started in repo-relative workspace `.` on branch `work/1778-v021-release-closeout`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1778.md`.
- Diagnostics Entry: `loom release readback` / `loom release resume` classified v0.21.0 publication state and confirmed only terminal carrier sync remained after publish.
- Verification Entry: Release/package checks, release-readback regression, ship-wrapper regression, npm smoke, npm pack dry-run, suite/fact-chain, PR metadata, hosted checks, controlled merge, release workflow, tag/GitHub Release/npm readback, issue/FR closeout, milestone closeout, and terminal carrier sync are complete.
- Lane Entry: release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1778.md
- Dynamic Truth: .loom/progress/WI-1778.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
