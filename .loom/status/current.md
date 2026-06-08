# Current Status

## Derived Fact Chain View

- Item ID: WI-1276
- Goal: Complete issue #1276 by splitting source-self review-run fixtures into a stable named source surface while preserving review contract assertions, aggregate `source-self-fixture` behavior, and full source profile compatibility.
- Scope: Allowed: `loom_check.py` source surface naming/runner contract for review-run fixtures; generated skills runtime `loom_check.py` parity sync; #1276 progress/status/PR metadata. Excluded: #1277/#1278/#1279/#1280 implementation, #1258 parent closeout, Round 4/Round 6+/Deferred roadmap work, release/package/workflow behavior, and scheduler-owned review/merge/closeout gates.
- Execution Path: issue #1276 -> branch `work/1276-source-self-review-run-fixtures` -> named `review-run` source surface -> generated skills runtime parity -> focused review-run validation -> aggregate source-self-fixture validation -> PR metadata/head binding -> scheduler-owned gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1276.md
- Review Entry: .loom/reviews/WI-1276.json
- Validation Entry: `git diff --check`; `python3 tools/py_compile_clean.py ...`; `python3 tools/loom.py suite validate --target . --item WI-1276 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1276 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1276 --json`; `python3 tools/loom.py skills check --target . --json`; `python3 tools/loom_check.py --profile source --source-surface review-run .`; `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`; root/demo runtime-state drift checks.
- Closing Condition: PR for #1276 is current-head reviewed and merged through scheduler-owned gate; issue #1276 is closed/completed; downstream #1277 may start only after #1276 merge/readback. Parent #1258 remains open until all children close.
- Current Checkpoint: merge
- Current Stop: Scheduler-owned current-head review and PR metadata gate inputs are recorded; PR #1374 is waiting for hosted checks and controlled merge.
- Next Step: Wait for hosted checks on the current PR head, run controlled merge, then perform post-merge readback and closeout sync for #1276 only.
- Blockers: None
- Latest Validation Summary: 2026-06-08 local validation passed: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py skills/loom-adopt/.loom-runtime/shared/scripts/loom_check.py skills/loom-build/.loom-runtime/shared/scripts/loom_check.py skills/loom-handoff/.loom-runtime/shared/scripts/loom_check.py skills/loom-init/.loom-runtime/shared/scripts/loom_check.py skills/loom-merge-ready/.loom-runtime/shared/scripts/loom_check.py skills/loom-pre-review/.loom-runtime/shared/scripts/loom_check.py skills/loom-resume/.loom-runtime/shared/scripts/loom_check.py skills/loom-retire/.loom-runtime/shared/scripts/loom_check.py skills/loom-review/.loom-runtime/shared/scripts/loom_check.py skills/loom-spec-review/.loom-runtime/shared/scripts/loom_check.py skills/loom-story/.loom-runtime/shared/scripts/loom_check.py tools/loom_check.py tools/check_loom_check_runtime_regressions.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1276 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1276 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1276 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface review-run .`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py runtime-state --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 examples/new-project/.loom/bin/loom_init.py runtime-state --target examples/new-project`.
- Recovery Boundary: #1276 owns only the review-run source surface split and directly required `loom_check.py` generated skills parity. Do not modify #1277/#1278/#1279/#1280 implementations, do not terminalize #1258, do not change release/package/workflow behavior, and do not run scheduler-owned review/guardian/controlled merge/closeout.
- Current Lane: source-self-review-run-fixtures

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: local command outputs in worker thread 019ea5b8-57e8-7123-b5ba-50c03a32385e
- Diagnostics Entry: resolved generated skills parity drift and resolved bootstrapped runtime manifest drift by reverting unmanifested `.loom/bin/loom_check.py` edits.
- Verification Entry: local validation passed before PR creation; hosted checks pending after push.
- Lane Entry: source-self-review-run-fixtures

## Sources

- Static Truth: .loom/work-items/WI-1276.md
- Dynamic Truth: .loom/progress/WI-1276.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
