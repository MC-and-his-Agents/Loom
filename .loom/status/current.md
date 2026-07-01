# Current Status

## Derived Fact Chain View

- Item ID: WI-1844
- Goal: 产品化 release readback 后的通用 release closeout-sync 入口。
- Scope: 实现 loom release closeout-sync dry-run/apply、CLI contract、README/README.zh-CN 和 CLI matrix；不发布、不 republish、不自动 merge、不新增 carrier/DSL。
- Execution Path: issue #1844 -> branch work/1844-release-closeout-sync -> PR -> v0.24.1 release
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1844.md
- Review Entry: .loom/reviews/WI-1844.json
- Validation Entry: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface release-readback; python3 tools/check_cli_contract.py --surface aggregate; loom release closeout-sync dogfood dry-run
- Closing Condition: PR merges, #1842/#1843/#1846 close, v0.24.1 publishes and release closeout-sync carrier is terminalized.
- Current Checkpoint: release
- Current Stop: Implementation PR #1847 merged into main at 62dd8e0abab37c80c19c3035c546fdf0bdb302ba after hosted gates and controlled merge. Release branch work/1845-v0.24.1-release is preparing v0.24.1 version/package/plugin metadata, release readiness evidence, PR body, and release gate inputs.
- Next Step: Open and gate the #1845 release PR, merge it after PR body/head/review/checks are stable, consume the main-push loom-cli-release run, then use `loom release closeout-sync --version v0.24.1 --item WI-1844 --apply` to terminalize repo carriers before issue and milestone closeout.
- Blockers: None recorded.
- Latest Validation Summary: #1847 merged at 62dd8e0abab37c80c19c3035c546fdf0bdb302ba after local PR gate, loom merge check/run, and hosted gates passed for head c3c62f46048e5387de49a6f473eb8921ed96a6e3. Release branch validation passed: py_compile_clean for release tools; version_surface_check; check_release_surface; check_npm_package with plugin hash 2ff7aa999840442fd179cbc8101b1d5fdd437889aab2516aebe90a66018e7cfb; check_cli_contract --surface release-readback; check_cli_contract --surface aggregate in 429.97s; npm pack --dry-run --json --ignore-scripts; suite validate/carrier/evidence; fact-chain. Release readback for v0.24.1 is missing/unpublished with tag, GitHub Release, and npm version unoccupied.
- Recovery Boundary: WI-1844 owns release closeout-sync wrapper, docs, tests, and v0.24.1 convergence only; no republishing, automatic merge, multi-repo batch, new DSL, or new carrier. Publication is only the authorized v0.24.1 release workflow after the release PR merges.
- Current Lane: release-pr

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1844 release closeout-sync work is active in `/Users/mc/dev/Loom.worktrees/1845-v0.24.1-release` on branch `work/1845-v0.24.1-release`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1844.md`.
- Diagnostics Entry: Release closeout-sync dogfood dry-run passes against the WI-1834 main worktree; the same command correctly fail-closes when run from the WI-1844 worktree against WI-1834 because the fact-chain item does not match.
- Verification Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/stamp_plugin_payload_metadata.py tools/version_surface_check.py`, `python3 tools/version_surface_check.py`, `python3 tools/check_release_surface.py`, `python3 tools/check_npm_package.py`, `python3 tools/check_cli_contract.py --surface release-readback`, `python3 tools/check_cli_contract.py --surface aggregate`, `npm pack --dry-run --json --ignore-scripts`, suite validate/carrier/evidence, fact-chain, release readback, hosted gates, and loom merge check/run passed for implementation PR #1847.
- Lane Entry: release-pr

## Sources

- Static Truth: .loom/work-items/WI-1844.md
- Dynamic Truth: .loom/progress/WI-1844.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
