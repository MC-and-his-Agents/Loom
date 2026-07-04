# Current Status

## Derived Fact Chain View

- Item ID: WI-1957
- Goal: 降低宿主 light-governance 默认采用成本。
- Scope: Batch covers #1957 default light-governance, #1958 installed-state slimming, #1959 workstation current pointer, and #1960 host-only ordinary closeout. Excludes #1962 batch closeout, #1964 existing host migration, #1965 planning taxonomy mapping, and #1966 release.
- Execution Path: issue #1957 anchor with covered issues #1958 #1959 #1960 -> branch work/1957-1960-host-tax-core -> PR #1971 -> hosted gate -> controlled merge -> GitHub issue closeout evidence.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1957.md
- Review Entry: .loom/reviews/WI-1957.json
- Validation Entry: py_compile; git diff --check; check_cli_contract adoption-host-metadata/workstation-registry/ship-wrapper; npm package payload checks; demo fixture drift; root verify; bootstrap regression; PR metadata readback/preflight.
- Closing Condition: PR #1971 merged, #1957 #1958 #1959 #1960 closed with host-only evidence, and host tax core behavior verified by local and hosted checks.
- Current Checkpoint: pre_review
- Current Stop: 实现层提交 4bc40a933e60b5b80cb0ab6f346d8df0951e547c 已完成；suite_not_applicable 已由 PR metadata、checkpoint/spec gate、hosted freeze admission、active fact-chain marker 和 build aggregate contract 一致消费。
- Next Step: 记录当前 head review，刷新 shadow，更新并 readback PR #1971 metadata，然后运行 PR gate/hosted checks。
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-04T11:39Z at 4bc40a933e60b5b80cb0ab6f346d8df0951e547c: python3 -m py_compile tools/check_cli_contract.py passed; git diff --check passed; python3 tools/check_cli_contract.py --surface aggregate passed in 540.20s after the suite_not_applicable build consumption contract fix. Earlier implementation validations at d07122cd5387ef46b5f6366fb2fb374ca887ad97 also passed: py_compile_clean for modified runtime/check files, git diff --check, pr-metadata-suite-not-applicable, runtime carrier suite_not_applicable adoption/spec-gate fixture, runtime-copy-parity, plugin-payload-hash with plugin_payload_hash 1a909ce725a9d41a75332af69296c4766634584295f944996c8a7d2cc308f763, and demo fixture drift.
- Recovery Boundary: WI-1957 owns PR #1971 host tax core batch for #1957/#1958/#1959/#1960 plus suite_not_applicable gate convergence needed by the batch. Excludes #1962 batch closeout, #1964 migration, #1965 taxonomy mapping, #1966 release, WebEnvoy-specific hardcoding, and downstream repo shims.
- Current Lane: host-tax-core

## Runtime Evidence

- Run Entry: 2026-07-04T04:37Z release branch `work/1955-v0.27.1-release` started from `main` merge commit `323e2300cc1a1e9b023b59a5588c4bab65adc51e` after implementation PR #1967 merged.
- Logs Entry: v0.27.1 release candidate updates `VERSION`, root `package.json`, and plugin payload metadata for the #1928/#1930 host friction patch.
- Diagnostics Entry: Local py_compile, diff check, version/release/npm package checks, npm pack dry-run, and skills release-check passed by 2026-07-04T04:43Z.
- Verification Entry: Pre-release readback confirmed tag `v0.27.1`, GitHub Release `v0.27.1`, and npm `@mc-and-his-agents/loom@0.27.1` were missing before release.
- Lane Entry: release-readiness

## Sources

- Static Truth: .loom/work-items/WI-1957.md
- Dynamic Truth: .loom/progress/WI-1957.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
