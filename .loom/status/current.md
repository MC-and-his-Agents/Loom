# Current Status

## Derived Fact Chain View

- Item ID: WI-965
- Goal: 让默认 loom_check 不再重写 stable demo fixture，并保留 demo bootstrap drift 检测能力。
- Scope: 调整 Makefile 与 CI 的 demo bootstrap 入口，使默认 check 在隔离临时目录重建并对比 examples/new-project；新增显式 sync 入口用于有意刷新 stable fixture；同步 harness 文档与 skill runtime references；不进入 #966/#968 或 CLI-first 主线。
- Execution Path: checks/demo-bootstrap-fixture-isolation
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-965.md
- Review Entry: .loom/reviews/WI-965.json
- Validation Entry: py_compile_clean; skills_surface check; make loom-demo-new-project-check; make loom-check; git status confirms examples/new-project remains unchanged
- Closing Condition: PR for #965 merged or merge-ready with default loom-check no longer dirtying examples/new-project while fixture drift remains detectable.
- Current Checkpoint: build checkpoint
- Current Stop: WI-965 implementation changes are in place and passed focused local validation.
- Next Step: Record spec and implementation review evidence, rerun final source loom_check if needed, commit, push, open PR, run PR gate and GitHub checks.
- Blockers: None recorded.
- Latest Validation Summary: Passed: make py-compile; python3 tools/skills_surface.py check after generate; make loom-demo-new-project-check; make loom-check -> loom_check OK, profile source, checked 40 source/distribution surfaces; git diff --check; node installer version bump check reports no installer behavior changes; git status confirms examples/new-project is not dirty.
- Recovery Boundary: WI-965 owns demo bootstrap fixture isolation in Makefile/CI/helper script, harness docs/reference sync, WI-965 carriers, and terminal predecessor WI-967 recovery update. Excludes #966 Node installer write isolation, #968 regression matrix, #969 review profile, #953 source self-check layering, and CLI-first mainline.
- Current Lane: build-validation

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/loom_check.py --profile source .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-965.md
- Dynamic Truth: .loom/progress/WI-965.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
