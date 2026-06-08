# Current Status

## Derived Fact Chain View

- Item ID: WI-1277
- Goal: Complete issue #1277 by splitting source-self merge, PR, merge-ready, checkpoint merge, stale review, CI bypass, required gate, and ruleset fixtures into a stable named `merge-gate` source surface while preserving fail-closed behavior, aggregate `source-self-fixture` behavior, and full source profile compatibility.
- Scope: Allowed: `loom_check.py` source surface naming/runner contract for merge-gate fixtures; generated skills runtime `loom_check.py` parity sync; WI-1277 progress/status/spec/evidence carriers; PR metadata for the #1277 PR. Excluded: #1278 closeout-reconciliation, #1279 retire-workspace, #1280 installed-runtime, #1258 parent closeout, Round 4/Round 6+/Deferred roadmap work, release/package/workflow behavior, and scheduler-owned review/merge/closeout gates.
- Execution Path: issue #1277 -> branch `work/1277-source-self-merge-gate-fixtures` -> named `merge-gate` source surface -> generated skills runtime parity -> focused merge-gate validation -> aggregate source-self-fixture validation -> PR metadata/head binding -> scheduler-owned gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1277.md
- Review Entry: .loom/reviews/WI-1277.json
- Validation Entry: `git diff --check`; focused Python compile for changed runtime/check files; `python3 tools/loom.py skills check --target . --json`; `python3 tools/loom_check.py --profile source --source-surface merge-gate .`; `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`; suite/fact-chain/carrier/shadow/PR metadata preflight/readback checks; hosted PR checks.
- Closing Condition: PR for #1277 is current-head reviewed and merged through scheduler-owned gate; issue #1277 is closed/completed; downstream #1278 may start only after #1277 merge/readback. Parent #1258 remains open until all children close.
- Current Checkpoint: build
- Current Stop: Local validation passed on branch `work/1277-source-self-merge-gate-fixtures`; `merge-gate` source surface has been added to the source-surface runner contract, generated skills runtime copies are synchronized, and repo carrier readback points at WI-1277.
- Next Step: Commit, push, create the #1277 PR, read back PR head/body metadata, wait for hosted checks, then stop at `waiting-scheduler-gate`.
- Blockers: None
- Latest Validation Summary: 2026-06-08 worker local validation passed for WI-1277 before PR creation: `git diff --check`; focused Python compile for `src/skills/shared/scripts/loom_check.py`, `skills/shared/scripts/loom_check.py`, `tools/loom_check.py`, `tools/check_loom_check_runtime_regressions.py`, and generated skill-local `loom_check.py` runtime copies; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --help` includes `merge-gate`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface merge-gate .` passed with `source_surface: merge-gate` after `merge-gate` step elapsed 352.49s and failures=0; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .` passed with aggregate evidence including `review-run` elapsed 823.38s, `merge-gate` elapsed 315.16s, and final `source-self-fixture` OK; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1277 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1277 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1277 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .` read back current item WI-1277 with no blocking failures; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1277 --write` passed.
- Recovery Boundary: Complete #1277 only. Do not implement #1278 closeout-reconciliation, #1279 retire-workspace, #1280 installed-runtime, #1258 parent closeout, release/package/workflow behavior, or scheduler-owned review/merge/closeout gates.
- Current Lane: source-self-merge-gate-fixtures

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: local command outputs in worker thread 019ea73d-a24c-70f3-8a15-5e4ec80e5e91
- Diagnostics Entry: `merge-gate` source surface added through canonical runtime and generated skills sync; no release/package/workflow behavior changes expected.
- Verification Entry: Local validation passed for focused `merge-gate`, aggregate `source-self-fixture`, generated skills parity, suite validate/evidence/carrier validate, fact-chain readback, and carrier refresh; PR metadata readback and hosted checks are pending PR creation.
- Lane Entry: source-self-merge-gate-fixtures

## Sources

- Static Truth: .loom/work-items/WI-1277.md
- Dynamic Truth: .loom/progress/WI-1277.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
