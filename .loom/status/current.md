# Current Status

## Derived Fact Chain View

- Item ID: WI-2012
- Goal: 修复 global-CLI metadata-only carrier refresh 对不存在 bootstrap manifest 的错误依赖。
- Scope: Issue #2012；主控线程 ownership 仅覆盖 carrier refresh 共享实现、对应 source/check_cli_contract 回归、生成副本和 WI-2012 carriers。保留 repo-local runtime manifest fail-closed，不修改 WebEnvoy 产品仓。
- Execution Path: issue #2012 -> branch work/2012-metadata-only-carrier-refresh -> targeted regression -> source validation -> PR gate -> merge
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-2012.md
- Review Entry: .loom/reviews/WI-2012.json
- Validation Entry: python3 -m py_compile src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py; python3 tools/loom_check.py --profile source --source-surface source-self-fixture; git diff --check
- Closing Condition: PR for #2012 merges with current-head review and hosted gates; Harbor #244 no longer fails carrier refresh because bootstrap manifest is intentionally absent.
- Current Checkpoint: merge
- Current Stop: Rebased onto origin/main; source and generated runtime validation passed. Current-head reviews must be refreshed before host merge.
- Next Step: Record WI-2012 spec and implementation reviews for the current head, then refresh PR metadata and run merge-ready.
- Blockers: None
- Latest Validation Summary: 2026-07-11 b0da48c9671361e04af9da95f2dfb887f8f472ad: git diff --check passed; py_compile passed; skills generated-tree check passed; make loom-demo-new-project-check passed; tools/check_npm_package.py passed; tools/check_cli_contract.py passed all 23 surfaces in 460.26s; tools/loom_check.py --profile source --source-surface source-self-fixture passed; Harbor HARBOR-241 source carrier-refresh reproduction passed without requiring bootstrap manifest.
- Recovery Boundary: Work item scaffolded at `.loom/work-items/WI-2012.md`.
- Current Lane: WI-2012 metadata-only carrier refresh correction

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: not_applicable
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-2012.md
- Dynamic Truth: .loom/progress/WI-2012.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
