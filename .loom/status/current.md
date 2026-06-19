# Current Status

## Derived Fact Chain View

- Item ID: WI-1621-1622-1623-1628-1638
- Goal: 冻结 milestone #14 前置安装合同：#1621 用户安装合同、#1622 installed-state 全局 provider 语义、#1623 旧安装面阻断策略、#1628 Codex 用户级 plugin 安装目标、#1638 宿主 AGENTS.md Loom Bootstrap 指令。
- Scope: 只修改 adoption/install/installed-state/host adapter/AGENTS bootstrap 合同文档与本 Work Item 载体；不实现 CLI 行为，不修改 VERSION、package.json、release evidence/docs、tools/check_cli_contract.py、generated skills 或 package surface。
- Execution Path: issue #1621/#1622/#1623/#1628/#1638 -> branch work/1621-1628-global-install-contracts -> docs contract PR -> targeted checks -> merge-ready -> issue closeout
- Workspace Entry: /Users/mc/dev/Loom-m14-contracts
- Recovery Entry: .loom/progress/WI-1621-1622-1623-1628-1638.md
- Review Entry: .loom/reviews/WI-1621-1622-1623-1628-1638.json
- Validation Entry: git diff --check; python3 tools/host_adapter_check.py; python3 tools/check_release_surface.py --surface forbidden-release-surface-patterns; python3 tools/check_cli_contract.py --surface adoption-host-metadata
- Closing Condition: PR documents the pure global CLI + Codex user-level plugin target, targeted checks pass, PR metadata/readback binds the current head, and issues #1621, #1622, #1623, #1628, and #1638 are closed or linked to the merged contract without starting the #1624+ implementation chain.
- Current Checkpoint: build checkpoint
- Current Stop: Contract docs are updated, suite path is formally `not_applicable`, and current-head review has been recorded with no findings.
- Next Step: Push, create the PR, read back PR metadata/current head, then run merge-ready gates.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-19T10:22Z on branch `work/1621-1628-global-install-contracts`: `git diff --check` passed; `python3 .loom/bin/loom_init.py fact-chain --target .` passed; `python3 tools/host_adapter_check.py` passed after preserving legacy vocabulary anchors; `python3 tools/check_release_surface.py` passed; `python3 tools/check_cli_contract.py --surface adoption-host-metadata` passed; `python3 tools/loom.py suite inspect --target . --item WI-1621-1622-1623-1628-1638 --json` reported `suite_path=not_applicable`; `python3 tools/loom_flow.py review record ...` recorded allow with no findings.
- Recovery Boundary: WI-1621-1622-1623-1628-1638 only: adoption/install/installed-state/host adapter/AGENTS bootstrap contract docs and this Work Item carrier. Excludes CLI implementation, root README release lane, VERSION, package.json, release evidence/docs, `tools/check_cli_contract.py`, generated skills, package surfaces, and the #1624+ implementation chain.
- Current Lane: milestone-14-contract-freeze

## Runtime Evidence

- Run Entry: 2026-06-19 WI-1621-1622-1623-1628-1638 milestone #14 contract freeze.
- Logs Entry: local command output retained in current Codex thread for `/Users/mc/dev/Loom-m14-contracts`.
- Diagnostics Entry: independent worktree and branch are active; changes are limited to adoption docs and Work Item carriers; root README and release/package surfaces remain untouched to avoid milestone/9 conflict.
- Verification Entry: `git diff --check`, `python3 .loom/bin/loom_init.py fact-chain --target .`, `python3 tools/host_adapter_check.py`, `python3 tools/check_release_surface.py`, `python3 tools/check_cli_contract.py --surface adoption-host-metadata`, `python3 tools/loom.py suite inspect --target . --item WI-1621-1622-1623-1628-1638 --json`, and `python3 tools/loom_flow.py review record ...` passed locally before push.
- Lane Entry: milestone-14-contract-freeze

## Sources

- Static Truth: .loom/work-items/WI-1621-1622-1623-1628-1638.md
- Dynamic Truth: .loom/progress/WI-1621-1622-1623-1628-1638.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
