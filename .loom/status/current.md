# Current Status

## Derived Fact Chain View

- Item ID: WI-1961
- Goal: Stabilize PR metadata and host consumer validation profiles for v0.28.0.
- Scope: Remove authored PR body head_sha as a merge-gate source of truth, bind review validation summaries by digest/source/locator, add host-consumer and carrier-only validation profile behavior, and sync generated runtime/plugin payload surfaces for PR #1970 covering #1961 and #1963.
- Execution Path: issue #1961 + #1963 -> branch work/1961-1963-gate-stabilizer -> PR #1970 -> hosted gate -> controlled merge -> GitHub issue closeout evidence.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1961.md
- Review Entry: .loom/reviews/WI-1961.json
- Validation Entry: py_compile_clean; git diff --check; check_cli_contract pr-metadata/ship-wrapper/pr-gate-target-readback/controlled-merge/governance-closeout/merge-wrapper/aggregate; skills release-check; PR metadata readback; hosted checks.
- Closing Condition: PR #1970 merged, #1961 and #1963 closed with evidence, and v0.28.0 gate stabilizer no longer requires authored PR body head_sha or source-repo validation for host-consumer/carrier-only profiles.
- Current Checkpoint: pre_review
- Current Stop: Gate stabilizer implementation and runtime carrier hash fixes are complete on branch work/1961-1963-gate-stabilizer for PR #1970; post-commit local validation passed and review metadata is being rebound to head 03bf63f0.
- Next Step: Record current-head review, refresh shadow evidence, push PR #1970, then rerun PR gate and hosted checks.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-04T07:07Z-07:17Z gate stabilizer post-commit validation: git diff --check passed; py_compile_clean passed for modified wrappers/runtime; demo bootstrap fixture-drift, canonicalization, aggregate passed; check_cli_contract surfaces pr-metadata and ship-wrapper passed; check_loom_check_runtime_regressions --surface demo-fixture-cleanliness passed; make repo-local-cli-fast GROUP=init-runtime passed; tools/loom.py skills release-check --json passed with plugin_payload_hash d0aa5b2419cad648e2729af859484b6c6d1e457b014c6040e1623d6201255a94; carrier refresh --write then --dry-run passed; shadow-parity --surface merge_ready passed; no tools/__pycache__ remained after wrapper execution.
- Recovery Boundary: WI-1961 owns only PR #1970 gate stabilizer scope for #1961/#1963: stable PR metadata, review validation summary binding, host-consumer/carrier-only validation profiles, generated runtime/plugin sync, local/hosted validation, and issue closeout evidence. Do not add #1957/#1958/#1959/#1960 host tax core, #1962 batch closeout, #1964 migration, #1965 taxonomy mapping, #1966 release, WebEnvoy-specific label hardcoding, or downstream repo-local tools/loom.py shim requirements.
- Current Lane: gate-stabilizer

## Runtime Evidence

- Run Entry: 2026-07-04T04:37Z release branch `work/1955-v0.27.1-release` started from `main` merge commit `323e2300cc1a1e9b023b59a5588c4bab65adc51e` after implementation PR #1967 merged.
- Logs Entry: v0.27.1 release candidate updates `VERSION`, root `package.json`, and plugin payload metadata for the #1928/#1930 host friction patch.
- Diagnostics Entry: Local py_compile, diff check, version/release/npm package checks, npm pack dry-run, and skills release-check passed by 2026-07-04T04:43Z.
- Verification Entry: Pre-release readback confirmed tag `v0.27.1`, GitHub Release `v0.27.1`, and npm `@mc-and-his-agents/loom@0.27.1` were missing before release.
- Lane Entry: release-readiness

## Sources

- Static Truth: .loom/work-items/WI-1961.md
- Dynamic Truth: .loom/progress/WI-1961.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
