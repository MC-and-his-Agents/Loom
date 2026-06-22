# Current Status

## Derived Fact Chain View

- Item ID: WI-1691
- Goal: 实现 `loom ship --apply`，在 gate 通过后执行 controlled merge，并完成默认 host-only closeout。
- Scope: 消费 #1690 的 `loom ship` dry-run surface 与 #1695 closeout policy；添加 root CLI apply 编排、safe metadata repair、controlled merge execute、host reconciliation sync、final closeout check，以及 focused wrapper regression coverage。Ownership constraints are limited to `tools/loom.py`, `tools/check_cli_contract.py`, `.loom/bootstrap/init-result.json`, `.loom/status/current.md`, `.loom/work-items/WI-1691.md`, `.loom/progress/WI-1691.md`, `.loom/progress/WI-1691-build-evidence.json`, `.loom/reviews/WI-1691.json`, `.loom/reviews/WI-1691.spec.json`, `.loom/specs/WI-1691/`, and PR metadata for #1691.
- Execution Path: issue #1691 -> branch `work/1691-ship-apply` -> focused CLI/test update -> PR -> controlled merge -> issue closeout.
- Workspace Entry: `/Users/mc/dev/Loom-WI-1691`
- Recovery Entry: .loom/progress/WI-1691.md
- Review Entry: .loom/reviews/WI-1691.json
- Validation Entry: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper --surface closeout-wrapper --surface ship-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1691 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1691`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1691`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1691 --build-evidence .loom/progress/WI-1691-build-evidence.json`.
- Closing Condition: PR is merged into main, issue #1691 is closed, and closeout confirms `loom ship --apply` merged and host-closed eligible work without creating a closeout PR by default.
- Current Checkpoint: build
- Current Stop: Implementation, focused wrapper validation, aggregate CLI contract, suite gates, fact-chain, state-check, evidence validation, carrier validation, build evidence, spec review, and implementation review are integrated for `loom ship --apply`.
- Next Step: Create PR metadata, enter merge-ready, controlled merge, and closeout.
- Blockers: None
- Latest Validation Summary: 2026-06-22 local validation on branch `work/1691-ship-apply`: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper --surface closeout-wrapper --surface ship-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface release-readback`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1691 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1691 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1691 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1691`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1691`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1691 --build-evidence .loom/progress/WI-1691-build-evidence.json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py flow review --target . --item WI-1691 --issue 1691 --pr 1706 --branch work/1691-ship-apply`.
- Recovery Boundary: WI-1691 owns `loom ship --apply` root wrapper orchestration and focused wrapper tests only. It does not implement `controlled-merge --closeout-run`, docs/skills convergence, milestone release publishing, or full closeout PR policy expansion.
- Current Lane: milestone-15-ship-apply

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1691 milestone #15 ship apply implementation in progress.
- Logs Entry: local command output retained in current Codex milestone #15 thread.
- Diagnostics Entry: `loom ship --apply` now preserves dry-run gates, executes controlled merge only after blockers clear, runs host reconciliation and final closeout check for eligible inline/host-only policies, and does not create a closeout PR by default.
- Verification Entry: 2026-06-22 focused local validation for diff check, py compile, ship-wrapper, adjacent wrapper surfaces, release-readback, aggregate, suite validate, suite evidence, suite carrier, fact-chain, state-check, build flow, spec review, and implementation review passed; PR #1706 metadata readback passed; hosted checks, merge-ready, controlled merge, and closeout remain.
- Lane Entry: milestone-15-ship-apply

## Sources

- Static Truth: .loom/work-items/WI-1691.md
- Dynamic Truth: .loom/progress/WI-1691.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
