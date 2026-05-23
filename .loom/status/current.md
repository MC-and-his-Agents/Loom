# Current Status

## Derived Fact Chain View

- Item ID: WI-966
- Goal: 隔离 Node installer regression 的 npm/dist/payload 写入，使同一 worktree 并发或相邻检查不会互删 node_modules、dist 或 payload。
- Scope: 新增 Node installer regression 受锁入口；让 CI 与 loom_check 通过同一 worktree-local installer regression lock 执行 npm ci、npm test 与 npm pack --dry-run；使用本次运行唯一 npm cache；同步 loom_check runtime purity 合同与 generated skill runtime copies；不进入 #968 回归矩阵、#965 demo fixture、#969 review profile、#953 source self-check 分层或 CLI-first 主线。
- Execution Path: checks/node-installer-regression-isolation
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-966.md
- Review Entry: .loom/reviews/WI-966.json
- Validation Entry: node packages/loom-installer/scripts/run-regression.mjs; npm --prefix packages/loom-installer run check:payload; python3 tools/skills_surface.py check; make loom-check; git status
- Closing Condition: PR for #966 merged or merge-ready with installer regression writes protected by a worktree-local lock, unique npm cache evidence, payload drift still detected, and issue/branch/worktree/PR/head/check state aligned.
- Current Checkpoint: review checkpoint
- Current Stop: WI-966 implementation merged origin/main through head 5db1941 with installer version 0.1.140; final make loom-check passed on the resolved merge head.
- Next Step: Push branch, update PR #983 to head 5db1941 plus final carrier-only evidence refresh, run PR gate and GitHub checks, then mark merge-ready or merge.
- Blockers: None recorded.
- Latest Validation Summary: Passed after merging origin/main: git diff --check; python3 tools/py_compile_clean.py tools/loom_check.py src/skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py skills/shared/scripts/loom_flow.py examples/new-project/.loom/bin/loom_check.py examples/new-project/.loom/bin/loom_flow.py; python3 tools/skills_surface.py check; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main -> OK (0.1.139 -> 0.1.140); python3 tools/version_surface_check.py; make loom-demo-new-project-check; node packages/loom-installer/scripts/run-regression.mjs; npm --prefix packages/loom-installer run check:payload -> payload drift OK d463c13f4ed042cbb438385d8a3956ed7fcb842fa125e2d5209beebabbe18981; make loom-check -> loom_check OK, profile source, checked 40 source/distribution surfaces.
- Recovery Boundary: WI-966 owns Node installer regression write isolation, worktree-local installer regression lock, unique npm cache handling, Node installer workflow routing, loom_check runtime integration, explicit demo runtime fixture sync caused by loom_check.py drift, WI-966 review/spec/status/shadow carriers, and WI-965 terminal predecessor progress. Excludes #968 regression matrix, #969 review profile, #953 source self-check layering, #965 feature work beyond terminal predecessor state, and CLI-first mainline.
- Current Lane: pr-prep

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make py-compile; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-966.md
- Dynamic Truth: .loom/progress/WI-966.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
