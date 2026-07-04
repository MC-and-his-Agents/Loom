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
- Current Checkpoint: release-readiness
- Current Stop: Release branch `work/1955-v0.27.1-release` has prepared v0.27.1 release metadata and WI-1955 release carriers after implementation PR #1967 merged at `323e2300cc1a1e9b023b59a5588c4bab65adc51e`.
- Next Step: Complete suite/fact-chain/shadow validation, author review records, open release PR, pass PR gate and hosted checks, merge, then read back Git tag, GitHub Release, npm package, and workflow state before closing issues and milestone #26.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-04T04:43Z on branch `work/1955-v0.27.1-release`: passed `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/check_release_surface.py tools/stamp_plugin_payload_metadata.py tools/version_surface_check.py`, `git diff --check`, `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`, `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`, `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`, `npm pack --dry-run --json --ignore-scripts`, and `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --target . --json`; pre-release readback for v0.27.1 returned missing/unpublished with no tag, GitHub Release, or npm version occupying the release path.
- Recovery Boundary: WI-1955 owns only the v0.27.1 release carrier, release metadata, readiness evidence, release PR, post-merge publication readback, and closeout for #1928, #1930, #1955, #1954, and milestone #26. Do not add #1933 temporary hardcoding, #1935/v0.28.0 host adoption tax, downstream repo-local `tools/loom.py` requirements, plugin surface version bumps, host adapter version bumps, release workflow rewrites, or manual tag/npm overwrites.
- Current Lane: release-readiness

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
