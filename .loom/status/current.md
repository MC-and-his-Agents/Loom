# Current Status

## Derived Fact Chain View

- Item ID: WI-964
- Goal: 为 loom_check 增加同 worktree single-flight lock，避免同一 worktree 两个全量检查同时进入重型写入段。
- Scope: 在 source/distribution 与 bootstrapped consumer loom_check 入口增加 per-worktree lock，记录 run_id、pid、started_at、command、cwd，提供 stale lock 恢复和 fail-fast owner/fallback 输出；不引入全机器跨仓锁，不阻止不同 worktree 并发，不扩大到 #967/#965/#966/#968。
- Execution Path: checks/loom-check-single-flight-lock
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-964.md
- Review Entry: .loom/reviews/WI-964.json
- Validation Entry: py_compile_clean for loom_check scripts; skills_surface check; CLI lock busy fixture; tools/loom_check.py --profile source .
- Closing Condition: PR for #964 merged or merge-ready with issue/branch/worktree/PR/head/check state aligned, and #964 no longer blocks #967/#965/#966/#968 on single-flight lock.
- Current Checkpoint: build
- Current Stop: Implemented and validated per-worktree loom_check single-flight lock across source and generated skills surfaces.
- Next Step: Record WI-964 code review, commit/push branch, open PR linked to #964, then consume checks and merge gate.
- Blockers: None recorded.
- Latest Validation Summary: Passed: git diff --check; python3 tools/py_compile_clean.py tools/loom_check.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py; python3 tools/skills_surface.py check; python3 tools/loom_flow.py adopt verify --target . --item WI-964; python3 tools/loom_flow.py shadow-parity --target .; python3 tools/loom_flow.py checkpoint build --target . --item WI-964; python3 tools/loom_check.py --profile source . -> OK, checked 40 source/distribution surfaces; lock residue absent after run.
- Recovery Boundary: Scope is #964 only: loom_check same-worktree single-flight lock, stale lock recovery, generated surface sync, WI-964 carriers, source validation evidence, and terminal WI-963 recovery update needed to consume the merged predecessor. Excludes #967 env/tmp cleanup, #965 fixture isolation, #966 installer isolation, #968 regression matrix, and #866/#873/#969/#953/CLI-first work.
- Current Lane: implementation-validated

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/loom_check.py --profile source .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-964.md
- Dynamic Truth: .loom/progress/WI-964.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
