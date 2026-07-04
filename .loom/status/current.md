# Current Status

## Derived Fact Chain View

- Item ID: WI-1955
- Goal: Publish v0.27.1 and complete the host friction patch milestone closeout.
- Scope: bump root Loom release authority to v0.27.1, align npm package and Codex plugin payload release metadata/hash, add v0.27.1 release readiness evidence, activate WI-1955 carriers, record spec/release review evidence, prepare and merge the release PR, then read back Git tag, GitHub Release, npm package, release workflow, issue closeout, and milestone #26 state.
- Execution Path: issue #1955 -> branch work/1955-v0.27.1-release -> release readiness evidence -> release PR -> main push release workflow -> release readback -> #1928/#1930/#1955/#1954/milestone #26 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1955.md
- Review Entry: .loom/reviews/WI-1955.json
- Validation Entry: release readback, release/package checks, npm package dry-run, suite/fact-chain, hosted checks, and post-merge release readback.
- Closing Condition: v0.27.1 tag, GitHub Release, npm @mc-and-his-agents/loom@0.27.1, plugin payload metadata/hash, #1928/#1930/#1955/#1954 closeout evidence, and milestone #26 readback are consistent.
- Current Checkpoint: closed_out
- Current Stop: WI-1955 release closeout synced for v0.27.1: release PR #1968 merged at c38b1f04aedba0d4c8c9d84a2cc062ead1d41299; published release readback consumed into terminal repo carrier state.
- Next Step: None.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-04T05:21Z closeout validation on branch `work/1955-v0.27.1-closeout`: `git diff --check` passed; `python3 tools/loom.py release readback --target . --version v0.27.1 --commit c38b1f04aedba0d4c8c9d84a2cc062ead1d41299 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json` returned published; `python3 tools/loom.py suite evidence validate --target . --item WI-1955 --json` passed; `python3 tools/loom.py suite carrier validate --target . --item WI-1955 --json` passed; release workflow `loom-cli-release` run 28695863790 succeeded; tag v0.27.1 resolves to c38b1f04aedba0d4c8c9d84a2cc062ead1d41299; GitHub Release https://github.com/MC-and-his-Agents/Loom/releases/tag/v0.27.1 is published; npm @mc-and-his-agents/loom@0.27.1 exists with latest=0.27.1.
- Recovery Boundary: WI-1955 owns only the v0.27.1 release carrier, release metadata, readiness evidence, release PR, post-merge publication readback, and closeout for #1928, #1930, #1955, #1954, and milestone #26. Do not add #1933 temporary hardcoding, #1935/v0.28.0 host adoption tax, downstream repo-local `tools/loom.py` requirements, plugin surface version bumps, host adapter version bumps, release workflow rewrites, or manual tag/npm overwrites.
- Current Lane: release-closeout-sync

## Runtime Evidence

- Run Entry: 2026-07-04T04:37Z release branch `work/1955-v0.27.1-release` started from `main` merge commit `323e2300cc1a1e9b023b59a5588c4bab65adc51e` after implementation PR #1967 merged.
- Logs Entry: v0.27.1 release candidate updates `VERSION`, root `package.json`, and plugin payload metadata for the #1928/#1930 host friction patch.
- Diagnostics Entry: Local py_compile, diff check, version/release/npm package checks, npm pack dry-run, and skills release-check passed by 2026-07-04T04:43Z.
- Verification Entry: Pre-release readback confirmed tag `v0.27.1`, GitHub Release `v0.27.1`, and npm `@mc-and-his-agents/loom@0.27.1` were missing before release.
- Lane Entry: release-readiness

## Sources

- Static Truth: .loom/work-items/WI-1955.md
- Dynamic Truth: .loom/progress/WI-1955.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
