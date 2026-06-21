# Current Status

## Derived Fact Chain View

- Item ID: WI-1690
- Goal: 新增 `loom ship --item <id> --pr <n> --intensity auto` dry-run 编排入口。
- Scope: 读取强度分类、binding precedence、metadata preflight、PR gate、controlled merge check 和 closeout policy；输出将执行的步骤、跳过理由、升级理由和 next action；不写 GitHub 或 repo carrier。Ownership constraints are limited to `tools/loom.py`, `tools/check_cli_contract.py`, `.loom/bootstrap/init-result.json`, `.loom/status/current.md`, `.loom/work-items/WI-1690.md`, `.loom/progress/WI-1690.md`, `.loom/progress/WI-1690-build-evidence.json`, `.loom/reviews/WI-1690.json`, `.loom/reviews/WI-1690.spec.json`, `.loom/specs/WI-1690/`, and PR metadata for #1690.
- Execution Path: issue #1690 -> branch `work/1690-ship-dry-run` -> focused CLI/test update -> PR -> controlled merge -> issue closeout.
- Workspace Entry: ./WI-1690/..
- Recovery Entry: .loom/progress/WI-1690.md
- Review Entry: .loom/reviews/WI-1690.json
- Validation Entry: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1690 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1690`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1690`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1690 --build-evidence .loom/progress/WI-1690-build-evidence.json`.
- Closing Condition: PR is merged into main, issue #1690 is closed, and closeout confirms ship dry-run behavior, non-mutating policy, host state, and Loom carriers agree.
- Current Checkpoint: merge
- Current Stop: Implementation, local validation, suite gates, fact-chain, state-check, build evidence, spec review, implementation review, PR creation, and PR metadata are integrated; hosted checks, merge-ready, controlled merge, and closeout remain.
- Next Step: Wait for hosted checks, rerun PR gate / merge-ready, then proceed to controlled merge and closeout.
- Blockers: None
- Latest Validation Summary: 2026-06-22 local validation on branch `work/1690-ship-dry-run`: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1690 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1690 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1690 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1690`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1690`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1690 --build-evidence .loom/progress/WI-1690-build-evidence.json`; spec review and implementation review recorded in `.loom/reviews/WI-1690.spec.json` and `.loom/reviews/WI-1690.json`.
- Recovery Boundary: WI-1690 owns `loom ship` dry-run orchestration and focused wrapper tests only. It does not implement `loom ship --apply`, controlled merge closeout-run, closeout carrier batching, issue closeout, or release publishing.
- Current Lane: milestone-15-ship-dry-run

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1690 milestone #15 ship dry-run implementation in progress.
- Logs Entry: local command output retained in current Codex milestone #15 thread.
- Diagnostics Entry: `loom ship` dry-run now summarizes PR metadata preflight, PR gate, controlled merge check, closeout policy, skipped post-merge closeout, and next action without mutating host or repo state.
- Verification Entry: 2026-06-22 local validation for diff check, py compile, ship-wrapper, aggregate, suite validate, suite evidence, suite carrier, fact-chain, state-check, build flow, spec review, implementation review, PR creation, and PR metadata passed; hosted gates remain.
- Lane Entry: milestone-15-ship-dry-run

## Sources

- Static Truth: .loom/work-items/WI-1690.md
- Dynamic Truth: .loom/progress/WI-1690.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
