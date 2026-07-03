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
- Current Checkpoint: merge
- Current Stop: v0.27.0 release PR #1952 is open at head `c633d31245be8d6faead02d2e974670475f11cee`; PR metadata readback and current-head review record are aligned, and local merge gate repair is in progress.
- Next Step: Re-run PR metadata readback and PR merge gate for PR #1952, rerun the failed hosted `loom-pr-merge-gate` after local gate passes, perform controlled merge, then wait for main-push release workflow and release readback before closing #1914/#1888/milestone #25.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-03T19:56Z on branch `work/1914-v0.27.0-release`: passed `py_compile_clean` for release tools, `git diff --check`, release/version/npm package checks, `npm pack --dry-run --json --ignore-scripts`, `tools/loom.py skills release-check --target . --json`, `tools/check_cli_contract.py --surface aggregate` (408.42s), suite validate/evidence/carrier validate for WI-1914, fact-chain for WI-1914, carrier refresh, shadow parity, purity-check, and build checkpoint; pre-release readback for v0.27.0 returned missing/unpublished with no tag, GitHub Release, npm version, or matching release workflow run occupying the release path. WI-1900 stale progress checkpoint was reconciled to its existing terminal closeout metadata so release gate purity has one active WI-1914 owner.
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
