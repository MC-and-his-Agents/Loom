# Current Status

## Derived Fact Chain View

- Item ID: WI-1694
- Goal: 收敛 README、skills 与 fixtures 到 intensity-aware ship 主路径，让普通用户以 loom ship 完成交付，不需要手动串 reconciliation、carrier closeout 或 closeout check。
- Scope: 更新 README / README.zh-CN Quick Start 与 agent prompt、merge-ready/closeout/retire 相关 skill 指引，以及 targeted CLI contract fixtures，说明 light/standard 默认使用 ship/inline/host-only closeout；reinforced/release/parent/milestone 等场景才升级到显式 closeout PR 或 release closeout。Ownership: main executor owns README, src skills, generated skills, plugin skills, WI-1694 carriers, and fixture integration; Goodall lane is read-only inventory only. 不得改变 CLI 行为，不扩大到 release #1696。
- Execution Path: issue #1694 -> branch work/1694-ship-entry-convergence -> PR -> controlled merge -> closeout
- Workspace Entry: ./WI-1694/..
- Recovery Entry: .loom/progress/WI-1694.md
- Review Entry: .loom/reviews/WI-1694.json
- Validation Entry: git diff --check; targeted docs/skills grep checks; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group merge-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1694 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1694; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1694
- Closing Condition: PR is merged into main, issue #1694 is closed, and closeout confirms docs/skills/fixtures point users to ship as the primary delivery path with closeout policy boundaries intact.
- Current Checkpoint: build checkpoint
- Current Stop: README, source skills, generated skills, plugin skills, minimal suite, and targeted fixture changes are implemented and locally validated.
- Next Step: Run implementation review, create PR for issue #1694, then proceed through PR gate, controlled merge, and closeout.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22 local validation passed: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group merge-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1694 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1694 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1694 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1694`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1694`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1694 --build-evidence .loom/progress/WI-1694-build-evidence.json`.
- Recovery Boundary: Work Item #1694 is active in `/Users/mc/dev/Loom-WI-1694` on branch `work/1694-ship-entry-convergence`; no work was performed in `/Users/mc/dev/Loom`.
- Current Lane: milestone-15-ship-entry-convergence

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1694 README / skills / fixture convergence completed in issue-scoped worktree `/Users/mc/dev/Loom-WI-1694`.
- Logs Entry: Local command output retained in current Codex milestone #15 thread; concise validation commands are listed in the Latest Validation Summary.
- Diagnostics Entry: `loom ship` is now documented as the ordinary delivery path after install/adoption; merge-ready and retire skills remain available as explicit preflight / diagnosis and local cleanup surfaces.
- Verification Entry: Targeted local validation passed for diff hygiene, Python compile, generated skills parity, ship-wrapper, merge-wrapper, suite validate, suite evidence validate, suite carrier validate, fact-chain, state-check, and build flow on 2026-06-22.
- Lane Entry: milestone-15-ship-entry-convergence

## Sources

- Static Truth: .loom/work-items/WI-1694.md
- Dynamic Truth: .loom/progress/WI-1694.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
