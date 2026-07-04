# Current Status

## Derived Fact Chain View

- Item ID: WI-1914
- Goal: Publish v0.27.0 and complete Workstation Upgrade and Repo Slimdown milestone closeout.
- Scope: bump root Loom CLI release authority to v0.27.0, align npm package and Codex plugin payload release metadata/hash, add v0.27.0 release readiness evidence, activate WI-1914 carriers, record spec/release review evidence, perform minimal stale carrier sync needed to unblock release gate purity, prepare and merge release PR, then read back GitHub Release/npm/tag/workflow and close out #1914, Phase #1888, and milestone #25 after terminal carrier closeout.
- Execution Path: issue #1914 -> branch work/1914-v0.27.0-release -> release readiness evidence -> release PR -> main push release workflow -> release readback -> #1914/#1888/milestone #25 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1914.md
- Review Entry: .loom/reviews/WI-1914.json
- Validation Entry: release readback, release/package checks, CLI contract checks, npm package dry-run, suite/fact-chain, hosted checks, and post-merge release readback.
- Closing Condition: v0.27.0 tag, GitHub Release, npm @mc-and-his-agents/loom@0.27.0, plugin payload metadata/hash, #1914/Phase #1888 closeout evidence, and milestone #25 readback are consistent.
- Current Checkpoint: closed_out
- Current Stop: v0.27.0 was published from release PR #1952 at merge commit `5b3eda8f401c0a229cc9df08ea61cc8c9873994b`; GitHub Release, npm package, release workflow, issue #1914, and Phase #1888 readback are complete.
- Next Step: Close milestone #25 after terminal carrier PR merges and final release readback confirms the repo carrier is terminal.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-03T23:49Z post-merge readback confirmed GitHub tag/release `v0.27.0`, npm `@mc-and-his-agents/loom@0.27.0`, successful `loom-cli-release.yml` run `28688150076`, successful `node-installer-release` and `loom-check` on merge commit `5b3eda8f401c0a229cc9df08ea61cc8c9873994b`, and published tarball plugin metadata stamped to the release commit.
- Recovery Boundary: WI-1914 owns v0.27.0 root release authority, package/plugin payload metadata/hash, release readiness evidence, release PR metadata, publication readback, terminal carrier closeout, and #1914/Phase #1888/milestone #25 closeout. It does not add new runtime behavior beyond FR-1 through FR-5, does not publish legacy installer, does not change plugin surface compatibility, and does not close issues before release readback plus terminal carrier closeout.
- Current Lane: release-readiness

## Runtime Evidence

- Run Entry: 2026-07-03T19:26Z v0.27.0 release branch initialized in `/Users/mc/dev/Loom` on branch `work/1914-v0.27.0-release`.
- Logs Entry: v0.27.0 release candidate prepared by bumping `VERSION`, `package.json`, and plugin payload release metadata/hash.
- Diagnostics Entry: Release surface, version surface, npm package aggregate, npm pack dry-run, aggregate CLI contract, skills release check, and pre-release readback passed by 2026-07-03T19:35Z.
- Verification Entry: Pre-release readback confirmed v0.27.0 tag, GitHub Release, and npm package version are unoccupied; npm latest remains 0.26.3.
- Lane Entry: release-readiness

## Sources

- Static Truth: .loom/work-items/WI-1914.md
- Dynamic Truth: .loom/progress/WI-1914.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
