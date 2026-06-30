# Current Status

## Derived Fact Chain View

- Item ID: WI-1806
- Goal: Provide shared PR intent profiles and easier governance carrier commands for docs/governance-only, closeout-only, release-only, carrier-sync-only, and fixture-only PRs.
- Scope: #1806 parent plus #1807-#1814 implementation and #1815 release convergence. Implementation ownership covered `tools/loom.py`, `tools/check_cli_contract.py`, `docs/methodology/harness/cli-command-matrix.md`, `.loom/reviews/WI-1806.spec.json`, `.loom/reviews/WI-1806.json`, `.loom/shadow/merge-ready-loom.json`, `.loom/shadow/closeout-loom.json`, and WI-1806 Loom carriers. Release ownership is limited to `VERSION`, `package.json`, `plugins/loom/.codex-plugin/plugin.json`, `docs/evidence/v0.22.0-release-readiness.md`, release PR metadata, release readback evidence, and WI-1806 carrier/status closeout. It does not close #1800/#1802 or rewrite `v0.21.2` evidence.
- Execution Path: issue tree #1806 -> branch `work/1806-pr-intent-carrier-ergonomics` -> shared `pr-intent prepare/check` implementation -> focused CLI contract fixtures -> PR #1817 merge -> branch `work/1815-v0.22.0-release` -> #1815 `v0.22.0` release readiness -> release PR -> publish/readback -> #1806 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1806.md
- Review Entry: .loom/reviews/WI-1806.json
- Validation Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/skills_surface.py tools/stamp_plugin_payload_metadata.py`; `python3 tools/check_cli_contract.py --surface pr-metadata`; `python3 tools/check_cli_contract.py --surface suite-contract`; `python3 tools/check_npm_package.py`; `python3 tools/loom.py skills release-check --json`; `python3 tools/check_release_surface.py`; `npm run test:package`; `python3 tools/loom.py pr-intent check --intent release-only ...`; `python3 tools/loom.py release readback --version v0.22.0 ...`; `python3 tools/loom_check.py --profile source .`; `git diff --check`.
- Closing Condition: PR #1817 for #1806 merges with current-head review and gate evidence, then #1815 completes `v0.22.0` release notes, version/package/plugin metadata and hash checks, pre-release checks, npm/package readback, release evidence, and #1806 closeout.
- Current Checkpoint: merge
- Current Stop: PR #1817 merged to `main` at `182dcef6d7011c05b3515afbd3ff87c9f585d63e` on 2026-06-30T10:13:40Z. PR #1819 merged to `main` at `888b8afda39506a41cc8bf33eb17878a4eb83fef` on 2026-06-30T10:36:52Z and released the `release-only` carrier-group scope fix. #1815 release convergence is active on branch `work/1815-v0.22.0-release` with local release validation passing at head `597e4234ff7315020a5e0b204929931780e6ae12`.
- Next Step: Bind current-head review for the release PR, rerun final `release-only` PR intent and merge checkpoint checks, push `work/1815-v0.22.0-release`, create/update the #1815 release PR, wait hosted checks, merge, then read back tag/GitHub Release/npm/workflow and close #1807-#1815 plus #1806.
- Blockers: None
- Latest Validation Summary: 2026-06-30 release candidate head `597e4234ff7315020a5e0b204929931780e6ae12` consumed #1819 from `origin/main` and passed: `python3 tools/loom.py pr-intent check --intent release-only --target . --item WI-1806 --issue 1815 --branch work/1815-v0.22.0-release --head-sha 597e4234ff7315020a5e0b204929931780e6ae12 --base origin/main --body-file .loom/runtime/pr/WI-1806-release-only-body.md --json`; `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/skills_surface.py tools/stamp_plugin_payload_metadata.py`; `python3 tools/check_cli_contract.py --surface pr-metadata`; `python3 tools/check_cli_contract.py --surface suite-contract`; `python3 tools/check_npm_package.py --surface plugin-payload-hash`; `python3 tools/check_npm_package.py --surface runtime-copy-parity`; `python3 tools/check_npm_package.py`; `python3 tools/loom.py skills release-check --json`; `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `npm run test:package`; `git diff --check`. `python3 tools/loom.py release readback --target . --version v0.22.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --commit 597e4234ff7315020a5e0b204929931780e6ae12 --release-judgment release_required --json --full-output` passed with verdict `missing` and gaps limited to `tag_missing`, `github_release_missing`, `npm_version_missing`, and `workflow_run_target_commit_missing`.
- Recovery Boundary: WI-1806 owns PR intent carrier ergonomics and #1815 `v0.22.0` release convergence only. It does not close #1800/#1802, does not rewrite `v0.21.2` release evidence, and does not make PR intent profiles bypass review, PR gate, merge-ready, release readback, host reconciliation, or closeout evidence.
- Current Lane: release-closeout

## Runtime Evidence

- Run Entry: 2026-06-30 WI-1806 release convergence resumed in repo-relative workspace `.` on branch `work/1815-v0.22.0-release`; local formal worktree locator is `/Users/mc/dev/Loom-1815-v0.22.0-release`.
- Logs Entry: Local validation and release readback output is retained in this Codex thread and summarized in `.loom/progress/WI-1806.md`.
- Diagnostics Entry: #1817 and #1819 are merged; #1800 is closed_out on `main`; v0.22.0 is unoccupied before release.
- Verification Entry: Release candidate version and plugin metadata are prepared; focused package/release checks, PR metadata/readback, and pre-merge release readback passed locally; current-head review, hosted checks, merge, publish readback, and closeout remain pending.
- Lane Entry: v0.22.0-release-convergence

## Sources

- Static Truth: .loom/work-items/WI-1806.md
- Dynamic Truth: .loom/progress/WI-1806.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
