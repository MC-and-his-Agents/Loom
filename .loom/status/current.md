# Current Status

## Derived Fact Chain View

- Item ID: WI-2012
- Goal: 修复 global-CLI metadata-only carrier refresh 对不存在 bootstrap manifest 的错误依赖。
- Scope: Issue #2012；仅修改共享 carrier refresh 语义、严格 installed-state 判定、回归测试和必要运行时副本；不修改 WebEnvoy 四仓。
- Execution Path: issue #2012 -> branch work/2012-metadata-only-carrier-refresh-rebuild -> targeted regression -> implementation handoff
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-2012.md
- Review Entry: .loom/reviews/WI-2012.json
- Validation Entry: python3 -m unittest test.work_item_audit_test.WorkItemAuditTest.test_metadata_only_global_cli_refresh_skips_only_intentionally_absent_manifest; python3 tools/loom_check.py --profile source --source-surface source-self-fixture
- Closing Condition: Current branch contains the validated repair and generated runtime copies; follow-on PR handling is decided separately.
- Current Checkpoint: build
- Current Stop: Implementation committed and pushed; no PR was created by request.
- Next Step: Create a replacement PR from this branch only after deciding how to close or retarget #2015.
- Blockers: No code blocker. Formal current-head review and PR metadata are intentionally absent because no PR was created.
- Latest Validation Summary: 2026-07-11: targeted metadata-only carrier refresh unittest, py_compile, generated-tree-drift, runtime-copy-parity, demo bootstrap sync, git diff --check, and loom_check installed-runtime passed. The source-self-fixture run completed without a captured final result because the runner stream detached; do not treat it as evidence.
- Recovery Boundary: WI-2012 owns only the metadata-only/global-CLI carrier refresh repair, strict installed-state checks, runtime copies, and its regression. WebEnvoy repositories and PR creation are excluded.
- Current Lane: replacement-pr-preparation

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
