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
- Current Stop: Contract docs are updated and draft PR #1644 is pushed with PR metadata readback passing on head `98cdd9e7e500768b5a37d49f0f802674e90fbdc9`; merge is waiting on milestone/9 #1292 closeout carrier convergence.
- Next Step: Wait for PR #1645 to merge #1292 closeout into `main`, then rebase this branch, refresh review and PR metadata, rerun hosted gates, and continue merge-ready/closeout.
- Blockers: PR #1644 is currently `CONFLICTING` because `main` carries active #1292 closeout state; upstream PR #1645 is open and its `loom-pr-merge-gate` is failing on review/validation-summary drift.
- Latest Validation Summary: 2026-06-19T10:35Z on branch `work/1621-1628-global-install-contracts`: local `git diff --check`, `python3 .loom/bin/loom_init.py fact-chain --target .`, `python3 tools/host_adapter_check.py`, `python3 tools/check_release_surface.py`, `npm --prefix packages/loom-installer run check:docs`, `python3 tools/check_cli_contract.py --surface adoption-host-metadata`, `python3 tools/loom.py suite inspect --target . --item WI-1621-1622-1623-1628-1638 --json`, `python3 tools/loom_flow.py checkpoint build --target . --item WI-1621-1622-1623-1628-1638 --output .loom/bootstrap/init-result.json`, `python3 tools/loom_flow.py review read --target . --item WI-1621-1622-1623-1628-1638 --review-file .loom/reviews/WI-1621-1622-1623-1628-1638.json`, and PR #1644 metadata update/readback passed; GitHub reports PR #1644 `mergeable=CONFLICTING` pending #1645.
- Recovery Boundary: WI-1621-1622-1623-1628-1638 only: adoption/install/installed-state/host adapter/AGENTS bootstrap contract docs and this Work Item carrier. Excludes CLI implementation, root README release lane, VERSION, package.json, release evidence/docs, `tools/check_cli_contract.py`, generated skills, package surfaces, and the #1624+ implementation chain.
- Current Lane: milestone-14-contract-freeze

## Runtime Evidence

- Run Entry: 2026-06-19 WI-1621-1622-1623-1628-1638 milestone #14 contract freeze.
- Logs Entry: local command output retained in current Codex thread for `/Users/mc/dev/Loom-m14-contracts`.
- Diagnostics Entry: independent worktree and branch are active; changes are limited to adoption docs and Work Item carriers; root README and release/package surfaces remain untouched to avoid milestone/9 conflict.
- Verification Entry: `git diff --check`, `python3 .loom/bin/loom_init.py fact-chain --target .`, `python3 tools/host_adapter_check.py`, `python3 tools/check_release_surface.py`, `npm --prefix packages/loom-installer run check:docs`, `python3 tools/check_cli_contract.py --surface adoption-host-metadata`, `python3 tools/loom.py suite inspect --target . --item WI-1621-1622-1623-1628-1638 --json`, `python3 tools/loom_flow.py checkpoint build --target . --item WI-1621-1622-1623-1628-1638 --output .loom/bootstrap/init-result.json`, `python3 tools/loom_flow.py review read --target . --item WI-1621-1622-1623-1628-1638 --review-file .loom/reviews/WI-1621-1622-1623-1628-1638.json`, and PR #1644 metadata readback passed; hosted merge remains blocked by #1645/#1292 carrier convergence.
- Lane Entry: milestone-14-contract-freeze

## Sources

- Static Truth: .loom/work-items/WI-1621-1622-1623-1628-1638.md
- Dynamic Truth: .loom/progress/WI-1621-1622-1623-1628-1638.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
