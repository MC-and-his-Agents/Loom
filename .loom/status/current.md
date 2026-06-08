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
- Current Stop: Worker scope is implemented and pushed to PR #1376; PR body machine carrier readback matches WI-1277, branch, current head, and no-release metadata; worker-owned local checks pass; hosted worker-owned checks pass; remaining hosted failures are scheduler-owned review/gate readiness for missing `.loom/reviews/WI-1277.json` and `.loom/reviews/WI-1277.spec.json`.
- Next Step: Scheduler performs current-head semantic/spec review, writes review artifacts if approved, reruns/consumes scheduler-owned PR merge gate and root governance checks, then owns controlled merge/readback/closeout.
- Blockers: Scheduler-owned review artifacts are intentionally absent: `.loom/reviews/WI-1277.json` and `.loom/reviews/WI-1277.spec.json`.
- Latest Validation Summary: 2026-06-08 worker validation on the current PR head: `git diff --check origin/main..HEAD`; focused Python compile for canonical/generated/runtime `loom_check.py` files plus `examples/new-project/.loom/bin/loom_check.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json`; `make loom-demo-new-project-check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface merge-gate .` passed with `merge-gate` elapsed 247.06s and failures=0; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .` passed with `review-run` elapsed 440.28s, `merge-gate` elapsed 210.42s, and aggregate OK; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1277 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1277 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1277 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .` read back current item WI-1277; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed. PR metadata preflight passed after body readback for the current head. Hosted checks: `py-compile`, `demo-bootstrap`, `repo-local-cli`, and `release-judgment` passed; `loom-check`, node installer `gate`, `root-self-governance`, and `loom-pr-merge-gate` are blocked by scheduler-owned missing review/spec review artifacts, with the earliest PR gate run also carrying stale pre-body-update metadata diagnostics that local readback has since cleared.
- Recovery Boundary: Complete #1277 only. Do not implement #1278 closeout-reconciliation, #1279 retire-workspace, #1280 installed-runtime, #1258 parent closeout, release/package/workflow behavior, or scheduler-owned review/merge/closeout gates.
- Current Lane: source-self-merge-gate-fixtures

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: local command outputs in worker thread 019ea73d-a24c-70f3-8a15-5e4ec80e5e91
- Diagnostics Entry: `merge-gate` source surface added through canonical runtime and generated skills sync; no release/package/workflow behavior changes expected.
- Verification Entry: Local validation passed for focused `merge-gate`, aggregate `source-self-fixture`, generated skills parity, suite validate/evidence/carrier validate, fact-chain readback, PR metadata readback, and worker-owned hosted checks; scheduler-owned review artifacts and final gate remain pending.
- Lane Entry: source-self-merge-gate-fixtures

## Sources

- Static Truth: .loom/work-items/WI-1277.md
- Dynamic Truth: .loom/progress/WI-1277.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
