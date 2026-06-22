# Current Status

## Derived Fact Chain View

- Item ID: WI-1692
- Goal: 为 controlled-merge 增加显式 closeout-run 串联，并消费 closeout policy，避免每个 implementation PR 合并后都被迫创建 closeout PR。
- Scope: 实现 root CLI merge run 的显式 --closeout-run / --closeout-mode 过渡路径；默认 merge 行为保持兼容；inline 复用 closeout run，host_only 只做 host reconciliation/readback，batched/full 模式在合并前 fail closed；补充 wrapper contract regression tests。Ownership limited to tools/loom.py, tools/check_cli_contract.py, .loom Work Item/progress/review/spec carrier, and PR #1707 metadata.
- Execution Path: issue #1692 -> branch work/1692-controlled-merge-closeout-run -> PR #1707 -> controlled merge -> closeout
- Workspace Entry: ./WI-1692/..
- Recovery Entry: .loom/progress/WI-1692.md
- Review Entry: .loom/reviews/WI-1692.json
- Validation Entry: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group merge-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group closeout-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group controlled-merge
- Closing Condition: PR #1707 is merged into main, issue #1692 is closed, and closeout confirms controlled-merge --closeout-run has current review, PR metadata, hosted checks, target branch, and issue state aligned.
- Current Checkpoint: build
- Current Stop: Implementation, focused wrapper validation, build evidence, spec review, implementation review, suite validation, fact-chain, and state-check are ready for PR gate refresh.
- Next Step: Commit and push WI-1692 carriers, refresh PR #1707 metadata to the pushed head, rerun PR gate and hosted checks, then continue to merge-ready.
- Blockers: none
- Latest Validation Summary: 2026-06-22 pre-carrier-commit validation passed: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group merge-wrapper; closeout-wrapper; ship-wrapper; controlled-merge; suite validate; suite evidence validate; suite carrier validate; fact-chain; state-check; flow review. Full aggregate remains intentionally not rerun after prior duplicated governance-closeout hang classification.
- Recovery Boundary: WI-1692 owns controlled-merge --closeout-run wrapper behavior, focused tests, build evidence, and its own review/merge carrier only; README/skills convergence remains #1694.
- Current Lane: milestone-15-controlled-merge-closeout-run

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1691 milestone #15 ship apply implementation in progress.
- Logs Entry: local command output retained in current Codex milestone #15 thread.
- Diagnostics Entry: `loom ship --apply` now preserves dry-run gates, executes controlled merge only after blockers clear, runs host reconciliation and final closeout check for eligible inline/host-only policies, and does not create a closeout PR by default.
- Verification Entry: 2026-06-22 focused local validation for diff check, py compile, ship-wrapper, adjacent wrapper surfaces, release-readback, aggregate, suite validate, suite evidence, suite carrier, fact-chain, state-check, build flow, spec review, and implementation review passed; PR #1706 metadata readback passed; workspace entry is repo-relative for hosted runner portability; hosted checks, merge-ready, controlled merge, and closeout remain.
- Lane Entry: milestone-15-ship-apply

## Sources

- Static Truth: .loom/work-items/WI-1692.md
- Dynamic Truth: .loom/progress/WI-1692.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
