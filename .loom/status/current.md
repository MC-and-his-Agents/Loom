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
- Current Stop: Local merge-ready and PR gate pass; the corrected native Work Item binding is awaiting a fresh hosted merge-gate run.
- Next Step: Consume the fresh hosted merge gate, run controlled merge, then release the fixed global CLI before returning to Harbor #244.
- Blockers: None
- Latest Validation Summary: 2026-07-11 ae0d2f40034b69d9b8601164165083fa70980860: `git diff --check origin/main...HEAD`, generated-tree drift, package/runtime-copy parity, demo bootstrap, source self-fixture, root self-adoption, merge-ready and local PR gate passed; unsupported-schema and symlink installed-state regressions now fail closed. Hosted merge gate must consume the corrected `Work Item: work_item:2012` PR binding.
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
