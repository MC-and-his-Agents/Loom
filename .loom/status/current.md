# Current Status

## Derived Fact Chain View

- Item ID: WI-1621-1622-1623-1628-1638
- Goal: 冻结 milestone #14 前置安装合同：#1621 用户安装合同、#1622 installed-state 全局 provider 语义、#1623 旧安装面阻断策略、#1628 Codex 用户级 plugin 安装目标、#1638 宿主 AGENTS.md Loom Bootstrap 指令。
- Scope: 只修改 adoption/install/installed-state/host adapter/AGENTS bootstrap 合同文档与本 Work Item 载体；不实现 CLI 行为，不修改 VERSION、package.json、release evidence/docs、tools/check_cli_contract.py、generated skills 或 package surface。
- Execution Path: issue #1621/#1622/#1623/#1628/#1638 -> branch work/1621-1628-global-install-contracts -> docs contract PR -> targeted checks -> merge-ready -> issue closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1621-1622-1623-1628-1638.md
- Review Entry: .loom/reviews/WI-1621-1622-1623-1628-1638.json
- Validation Entry: git diff --check; python3 tools/host_adapter_check.py; python3 tools/check_release_surface.py --surface forbidden-release-surface-patterns; python3 tools/check_cli_contract.py --surface adoption-host-metadata
- Closing Condition: PR documents the pure global CLI + Codex user-level plugin target, targeted checks pass, PR metadata/readback binds the current head, and issues #1621, #1622, #1623, #1628, and #1638 are closed or linked to the merged contract without starting the #1624+ implementation chain.
- Current Checkpoint: build checkpoint
- Current Stop: Hosted gate blocker class is reduced to missing/stale suite evidence, task carrier, and shadow carrier refresh; local fixes now validate.
- Next Step: Commit suite carrier/evidence refresh, refresh review and PR metadata, push, then rerun hosted gates.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-19T11:16Z in `/Users/mc/dev/Loom-m14-contracts` on branch `work/1621-1628-global-install-contracts`: `git diff --check` passed; `python3 .loom/bin/loom_init.py fact-chain --target .` passed; `python3 tools/host_adapter_check.py` passed; `python3 tools/check_release_surface.py` passed; `npm --prefix packages/loom-installer run check:docs` passed; `python3 tools/check_cli_contract.py --surface adoption-host-metadata` passed; `python3 tools/loom.py suite inspect --target . --item WI-1621-1622-1623-1628-1638 --json` passed; `python3 tools/loom.py suite validate --target . --item WI-1621-1622-1623-1628-1638 --json` returned `not_applicable` with no blocking gaps; `python3 tools/loom.py suite evidence validate --target . --item WI-1621-1622-1623-1628-1638 --json` passed; `python3 tools/loom.py suite carrier validate --target . --item WI-1621-1622-1623-1628-1638 --json` passed; `python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking` passed.
- Recovery Boundary: WI-1621-1622-1623-1628-1638 only: adoption/install/installed-state/host adapter/AGENTS bootstrap contract docs and this Work Item carrier. Excludes CLI implementation, root README release lane, VERSION, package.json, release evidence/docs, `tools/check_cli_contract.py`, generated skills, package surfaces, and the #1624+ implementation chain.
- Current Lane: milestone-14-contract-freeze

## Runtime Evidence

- Run Entry: 2026-06-19 WI-1621-1622-1623-1628-1638 milestone #14 contract freeze.
- Logs Entry: local command output retained in current Codex thread for `/Users/mc/dev/Loom-m14-contracts`.
- Diagnostics Entry: independent worktree and branch are active; latest `origin/main` includes #1292/#1645 closeout; #14 changes remain limited to adoption docs and Work Item carriers.
- Verification Entry: `git diff --check`, `python3 .loom/bin/loom_init.py fact-chain --target .`, `python3 tools/host_adapter_check.py`, `python3 tools/check_release_surface.py`, `npm --prefix packages/loom-installer run check:docs`, `python3 tools/check_cli_contract.py --surface adoption-host-metadata`, `python3 tools/loom.py suite inspect --target . --item WI-1621-1622-1623-1628-1638 --json`, `python3 tools/loom.py suite validate --target . --item WI-1621-1622-1623-1628-1638 --json`, `python3 tools/loom.py suite evidence validate --target . --item WI-1621-1622-1623-1628-1638 --json`, `python3 tools/loom.py suite carrier validate --target . --item WI-1621-1622-1623-1628-1638 --json`, and `python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking` were consumed after merging latest `origin/main`; `suite validate` is expected to return `not_applicable` for this docs-only contract freeze.
- Lane Entry: milestone-14-contract-freeze

## Sources

- Static Truth: .loom/work-items/WI-1621-1622-1623-1628-1638.md
- Dynamic Truth: .loom/progress/WI-1621-1622-1623-1628-1638.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
