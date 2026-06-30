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
- Current Checkpoint: closeout
- Current Stop: PR #1820 merged to `main` at `aef7d796c20ae277dab733974338fc83d2a78d0a` on 2026-06-30T11:07:46Z. The `loom-cli-release` main-push run `28439804189` completed successfully at 2026-06-30T11:12:31Z and published `v0.22.0` to GitHub Release and npm.
- Next Step: Merge the closeout-only carrier sync PR, then close #1807-#1815 and parent #1806 after host readback confirms the terminal carrier is on `main`.
- Blockers: None
- Latest Validation Summary: 2026-06-30 post-merge readback for `v0.22.0` passed at merge commit `aef7d796c20ae277dab733974338fc83d2a78d0a`: `python3 tools/loom.py release readback --target . --version v0.22.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --commit aef7d796c20ae277dab733974338fc83d2a78d0a --release-judgment release_required --json --full-output` found the tag, GitHub Release, npm package, latest dist-tag, and successful `loom-cli-release` run `28439804189`; it only reported `carrier_not_terminal`, which this closeout-only PR resolves. Published package payload readback from `npm pack @mc-and-his-agents/loom@0.22.0` confirmed `source_package_version=0.22.0`, `plugin_payload_version=0.22.0`, `source_git_sha=aef7d796c20ae277dab733974338fc83d2a78d0a`, `plugin_payload_hash=61aa354525d28d00e83be98a7f2666765e390b8dd767d14bf141dac8b7896963`, and matching computed hash. Isolated prefix install smoke passed with `loom version --json` and `loom help --json`.
- Recovery Boundary: WI-1806 owns PR intent carrier ergonomics and #1815 `v0.22.0` release convergence only. It does not close #1800/#1802, does not rewrite `v0.21.2` release evidence, and does not make PR intent profiles bypass review, PR gate, merge-ready, release readback, host reconciliation, or closeout evidence.
- Current Lane: closeout-sync

## Runtime Evidence

- Run Entry: 2026-06-30 WI-1806 release convergence resumed in repo-relative workspace `.` on branch `work/1815-v0.22.0-release`; local formal worktree locator is `/Users/mc/dev/Loom-1815-v0.22.0-release`.
- Logs Entry: Local validation and release readback output is retained in this Codex thread and summarized in `.loom/progress/WI-1806.md`.
- Diagnostics Entry: #1817, #1819, and #1820 are merged; #1800 is closed_out on `main`; v0.22.0 is published and read back from GitHub Release and npm.
- Verification Entry: Release candidate validation, hosted checks, controlled merge, main-push release workflow, tag/GitHub Release/npm readback, published package payload hash, and isolated install smoke passed. Closeout-only carrier sync PR and issue closeout remain pending.
- Lane Entry: v0.22.0-closeout-sync

## Sources

- Static Truth: .loom/work-items/WI-1806.md
- Dynamic Truth: .loom/progress/WI-1806.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
