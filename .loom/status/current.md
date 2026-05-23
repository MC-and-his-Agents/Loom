# Current Status

## Derived Fact Chain View

- Item ID: WI-967
- Goal: 清理 loom_check 默认运行中的固定临时路径与宿主环境污染，避免跨仓或当前 Codex App/GitHub 环境影响 source self-check 结果。
- Scope: 替换固定 /tmp 缺失目标样本为本次运行唯一 absent path；默认 subprocess 环境剥离 CODEX_*、LOOM_CODEX_APP_REVIEW_*、CI/CODEX_CI 与 GitHub token 等宿主变量；保留 env= 显式 fixture 注入能力、HOME/PATH/gh keyring 行为和既有显式 live smoke 语义；不进入 #965/#966/#968 或 review profile/source self-check 分层。
- Execution Path: checks/loom-check-runtime-purity
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-967.md
- Review Entry: .loom/reviews/WI-967.json
- Validation Entry: py_compile_clean for loom_check scripts; skills_surface check; fixed tmp/env purity self-check; tools/loom_check.py --profile source .
- Closing Condition: PR for #967 merged or merge-ready with issue/branch/worktree/PR/head/check state aligned, and default loom_check no longer inherits host/Codex env or fixed /tmp missing target pollution.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-967 implementation head 3a633197a57c8b6e7d55f41464d3ff4b199b8c24 is validated locally and ready for refreshed review evidence plus PR checks.
- Next Step: Record refreshed spec and implementation reviews on 3a633197a57c8b6e7d55f41464d3ff4b199b8c24, commit carrier updates, push, rerun PR gate/checks, then merge or record blocker.
- Blockers: None recorded.
- Latest Validation Summary: Head 3a633197a57c8b6e7d55f41464d3ff4b199b8c24 passed: py_compile_clean for loom_check scripts; skills_surface check; runtime purity self-check; checkpoint admission/build/merge; spec review record; implementation review record; adopt verify; shadow parity; python3 tools/loom_check.py --profile source . on implementation head 02ea65939ae3947ed3cf7175ce9e716973ffa2df; installer version bump check 0.1.136 -> 0.1.137 against origin/main; git diff --check; no loom_check lock; no pycache remains. Pending: refreshed review carrier commit, push, PR gate, host checks.
- Recovery Boundary: WI-967 owns env/tmp purity changes in loom_check runtime surfaces, required installer version metadata, and associated Loom carriers; #965/#966/#968 remain separate work items.
- Current Lane: pr-prep

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/loom_check.py --profile source .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-967.md
- Dynamic Truth: .loom/progress/WI-967.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
