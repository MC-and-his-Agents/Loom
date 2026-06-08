# WI-1276 Plan

- Suite path: minimal

## Implementation

- Phase 1: Add `SOURCE_SURFACE_REVIEW_RUN`, split review-run fixture logic into `check_review_run_fixture()`, and give it the stable `review-run-fixture` category.
- Phase 2: Preserve aggregate behavior by making `source-self-fixture` include `review-run` while keeping full source profile coverage.
- Phase 3: Synchronize generated skills runtime `loom_check.py` copies and avoid unmanifested bootstrapped `.loom/bin` edits.
- Phase 4: Bind WI-1276 carriers and PR metadata to the current head, then stop for scheduler-owned gate.

## Deferred Items

- #1277 merge-gate fixtures remain deferred until #1276 merge/readback. Statement: deferred is not completed.
- #1278 closeout/reconciliation fixtures remain deferred until #1277 merge/readback. Statement: deferred is not completed.
- #1279 retire/workspace fixtures remain deferred until #1278 merge/readback. Statement: deferred is not completed.
- #1280 installed-runtime fixtures remain deferred until #1279 merge/readback. Statement: deferred is not completed.
- #1258 parent closeout remains deferred until all child issues close. Statement: deferred is not completed.

## Validation

- S1 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface review-run .`
- S2 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- S3 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json`, `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py runtime-state --target .`, and `PYTHONDONTWRITEBYTECODE=1 python3 examples/new-project/.loom/bin/loom_init.py runtime-state --target examples/new-project`
- AC-1 -> structural check: `python3 tools/loom_check.py --profile source --help` includes `review-run`.
- AC-2 -> test evidence: aggregate `source-self-fixture` output shows and passes the `review-run` step.
- AC-3 -> test evidence: focused `review-run` fixture passes.
- AC-4 -> test evidence: generated skills parity passes.
- AC-5 -> test evidence: root/demo runtime-state commands pass.

## Minimal Path Applicability Records

- full-path-artifacts not_applicable rationale: #1276 is a bounded runtime fixture split with GitHub issue acceptance, focused source-surface checks, generated parity checks, and current Work Item carriers; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for this slice. consumer boundary: review, merge-ready, and closeout consume issue #1276, `.loom/work-items/WI-1276.md`, `.loom/progress/WI-1276.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, and validation outputs. recheck condition: if scope expands into downstream Round 5 surfaces, release/package/workflow behavior, external host actions, or multi-module design beyond `loom_check.py` fixture surface selection, author the full suite before review.
