# WI-1277 Plan

- Suite path: minimal

## Implementation

- Phase 1: Add `SOURCE_SURFACE_MERGE_GATE` and expose `merge-gate` through the existing `--source-surface` choices and profile contract anchors.
- Phase 2: Preserve aggregate behavior by making `source-self-fixture` include `merge-gate` alongside `review-run` and the remaining source-self fixture steps.
- Phase 3: Assign the existing daily execution gate fixture container to source surface `merge-gate` with step name `merge-gate`, preserving existing fail-closed scenario assertions without changing merge/PR/merge-ready semantics.
- Phase 4: Synchronize generated skills runtime `loom_check.py` copies with canonical source through the established skills generation command.
- Phase 5: Bind WI-1277 carriers and PR metadata to the current head, then stop for scheduler-owned gate.

## Deferred Items

- #1278 closeout/reconciliation fixtures remain deferred until #1277 merge/readback. Statement: deferred is not completed.
- #1279 retire/workspace fixtures remain deferred until #1278 merge/readback. Statement: deferred is not completed.
- #1280 installed-runtime fixtures remain deferred until #1279 merge/readback. Statement: deferred is not completed.
- #1258 parent closeout remains deferred until all child issues close. Statement: deferred is not completed.

## Validation

- S1 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface merge-gate .`
- S2 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- S3 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json`
- AC-1 -> structural check: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --help` includes `merge-gate`.
- AC-2 -> test evidence: aggregate `source-self-fixture` output shows and passes the `merge-gate` step.
- AC-3 -> test evidence: focused `merge-gate` fixture passes while preserving existing fail-closed scenario assertions.
- AC-4 -> test evidence: generated skills parity passes.
- AC-5 -> diff/readback evidence: changed files stay within allowed runtime/carrier scope and no release/package/workflow files change.
- AC-5 -> structural check: `git diff --name-only` and PR metadata readback confirm no release, package, workflow, #1278, #1279, #1280, or #1258 closeout behavior changes.

## Minimal Path Applicability Records

- full-path-artifacts not_applicable rationale: #1277 is a bounded runtime fixture split with GitHub issue acceptance, focused source-surface checks, generated parity checks, and current Work Item carriers; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for this slice. consumer boundary: review, merge-ready, and closeout consume issue #1277, `.loom/work-items/WI-1277.md`, `.loom/progress/WI-1277.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, validation outputs, and hosted check readback. recheck condition: if scope expands into downstream Round 5 surfaces, release/package/workflow behavior, external host actions, or multi-module design beyond `loom_check.py` fixture surface selection, author the full suite before review.
