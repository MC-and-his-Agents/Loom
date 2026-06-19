# Current Status

## Derived Fact Chain View

- Item ID: WI-1452
- Goal: 让 controlled-merge 在 required checks 全绿时仍阻断当前 PR head 上已触发的失败或未完成非 required checks。
- Scope: Issue #1452 only: implement triggered check rollup consumption in controlled-merge, expose triggered_check_rollup JSON, add targeted fixtures/docs, sync generated/runtime/demo surfaces, and do not mutate live branch protection, release, #1292, #1293, or parent #1285 closeout.
- Execution Path: issue #1452 -> branch work/1452-controlled-merge-triggered-checks -> PR #1614 -> hosted checks -> controlled merge -> issue closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1452.md
- Review Entry: .loom/reviews/WI-1452.json
- Validation Entry: python3 -m py_compile src/skills/shared/scripts/loom_flow.py tools/check_cli_contract.py examples/new-project/.loom/bin/loom_flow.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge; python3 tools/skills_surface.py check --surface generated-tree-drift; make loom-demo-new-project-check; git diff --check; PR metadata readback; hosted checks
- Closing Condition: PR #1614 passes local and hosted gates, controlled merge consumes required and triggered check readbacks, #1452 is closed, and later #1292/#1293 consume the completed behavior without scope expansion.
- Current Checkpoint: merge
- Current Stop: WI-1452 implementation and formal reviews are recorded for implementation head 07bb4651cc662c008e2855f877fa6ee7844cc931; carrier-only sync is ready for PR #1614 hosted check readback.
- Next Step: Commit and push carrier-only sync, rerun/read back hosted checks, then run controlled-merge check and merge #1452 before continuing to #1292.
- Blockers: None recorded
- Latest Validation Summary: 2026-06-19: py_compile passed for src/skills/shared/scripts/loom_flow.py, tools/check_cli_contract.py, and examples/new-project/.loom/bin/loom_flow.py; merge-wrapper and controlled-merge CLI contract surfaces passed; generated-tree-drift passed; make loom-demo-new-project-check passed after fixture sync; git diff --check passed; PR #1614 metadata-update/readback passed for WI-1452 at head 07bb4651cc662c008e2855f877fa6ee7844cc931.
- Recovery Boundary: WI-1452 only: triggered-check rollup behavior, targeted fixtures/docs, generated/runtime/demo sync, PR #1614 metadata/gate evidence. Excludes live branch protection mutation, #1292 fixture closeout, #1293 release convergence, parent #1285 closeout, VERSION/tag/GitHub Release/npm publish.
- Current Lane: controlled-merge-triggered-checks

## Runtime Evidence

- Run Entry: 2026-06-19 WI-1596 v0.15.0 release-required closeout preparation
- Logs Entry: local command output retained in current Codex milestone/13 thread
- Diagnostics Entry: #1596 release_required closeout is complete; v0.15.0 tag, GitHub Release, npm package, and release workflow readback are consistent.
- Verification Entry: pre-merge release validation passed for the WI-1596 v0.15.0 release payload and PR #1612 metadata; post-merge release readback classified v0.15.0 as published and isolated npm exec smoke reported repo_version v0.15.0.
- Lane Entry: milestone-13-release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1452.md
- Dynamic Truth: .loom/progress/WI-1452.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
