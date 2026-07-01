# Current Status

## Derived Fact Chain View

- Item ID: WI-1834
- Goal: 实现单仓 Loom 运行时升级维护流程，并为 v0.24.0 发布准备标准、低摩擦、可验证的 repo runtime pin 升级路径。
- Scope: 覆盖 issue #1834-#1838 的 runtime-upgrade status/prepare/check/closeout、loom -v/--version、CLI help/matrix、英文/中文 README、Codex plugin/cache advisory guidance、runtime copy/plugin metadata/hash 与示例 fixture 同步；不包含多仓批量升级或跳过治理。
- Execution Path: issue tree #1834 -> branch work/1834-runtime-upgrade -> PR #1839 -> merge -> v0.24.0 release #1838 -> closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1834.md
- Review Entry: .loom/reviews/WI-1834.json
- Validation Entry: make py-compile; make loom-demo-new-project-check; python3 tools/check_cli_contract.py --surface aggregate; python3 tools/check_npm_package.py; python3 tools/check_npm_package.py --surface runtime-copy-parity; python3 tools/loom.py skills release-check --json; PR metadata preflight/readback for PR #1839
- Closing Condition: PR #1839 merges to main, #1835-#1837 implementation scope is closed, v0.24.0 release issue #1838 publishes and reads back GitHub/npm/package/plugin metadata, #1834-#1838 and milestone #20 close, and repo carrier closeout consumes the final facts.
- Current Checkpoint: closed
- Current Stop: v0.24.0 implementation PR #1839 and release PR #1840 are merged; main release workflow published tag v0.24.0, GitHub Release, and npm package 0.24.0; terminal closeout metadata is recorded for WI-1834.
- Next Step: None.
- Blockers: None recorded.
- Latest Validation Summary: #1839 merged at b795a83800a1c08ef667036371965f13bc811611 after hosted loom-check, node-installer-pr-gate, loom-pr-merge-gate, and release-judgment passed for head b66e6086da0908ed04c5e7d2397e44fe05f527fa. #1840 merged at 1aafb7fb031d997b7b497e277a525e308f766407 after release-only PR gate, pr-intent check, shadow parity, release surface, package, and hosted checks passed. Main release workflow 28493294251 published tag v0.24.0, GitHub Release, and npm @mc-and-his-agents/loom@0.24.0; release readback passed for tag/release/npm/workflow/package surfaces with only carrier terminalization pending before this sync.
- Recovery Boundary: WI-1834 owns single-repo runtime-upgrade maintenance flow implementation and v0.24.0 release convergence only. Do not add multi-repo batch mode, do not mutate user-level Codex plugin/cache from repo PR commands, do not lower review/PR gate/head binding/CI/release/closeout requirements, and do not represent plugin/cache advisory state as a repo merge fact.
- Current Lane: closed_out

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1834 runtime-upgrade work resumed in `/Users/mc/dev/Loom.worktrees/1834-runtime-upgrade` on branch `work/1834-runtime-upgrade`.
- Logs Entry: Validation output and hosted check classification are retained in this Codex thread and summarized in `.loom/progress/WI-1834.md`.
- Diagnostics Entry: Hosted `loom-pr-merge-gate` first failed because it read stale PR body/head metadata before update propagation and because repo fact-chain/review still pointed at WI-1805. WI-1834 fact-chain and review carriers are now refreshed and must be consumed by a new gate run.
- Verification Entry: `make py-compile`, `make loom-demo-new-project-check`, `python3 tools/check_cli_contract.py --surface aggregate`, package checks, release-check, diff whitespace, PR metadata preflight/readback, and hosted `loom-check` component jobs passed for current or immediately preceding stable inputs.
- Lane Entry: closed_out

## Sources

- Static Truth: .loom/work-items/WI-1834.md
- Dynamic Truth: .loom/progress/WI-1834.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
