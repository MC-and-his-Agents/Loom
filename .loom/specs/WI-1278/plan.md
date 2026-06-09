# WI-1278 Plan

- Suite path: minimal

## Implementation

- Phase 1: Add `SOURCE_SURFACE_CLOSEOUT_RECONCILIATION` and expose `closeout-reconciliation` through the existing `--source-surface` choices and profile contract anchors.
- Phase 2: Preserve aggregate behavior by making `source-self-fixture` include `closeout-reconciliation` alongside `review-run`, `merge-gate`, and the remaining source-self fixture steps.
- Phase 3: Move closeout check/sync, reconciliation audit, reconciliation sync dry-run, status closeout payload checks, and synthetic closeout reconciliation payload samples into a focused `closeout-reconciliation` fixture runner while preserving fail-closed behavior.
- Phase 4: Synchronize generated skills runtime `loom_check.py` copies with canonical source through the established skills generation command and refresh the demo runtime fixture.
- Phase 5: Bind WI-1278 carriers and PR metadata to the current head, then stop for scheduler-owned gate.

## Deferred Items

- #1279 retire/workspace fixtures remain deferred until #1278 merge/readback. Statement: deferred is not completed.
- #1280 installed-runtime fixtures remain deferred until #1279 merge/readback. Statement: deferred is not completed.
- #1258 parent closeout remains deferred until all child issues close. Statement: deferred is not completed.

## Validation

- S1 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface closeout-reconciliation .`
- S2 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- S3 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json`
- AC-1 -> structural check: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --help` includes `closeout-reconciliation`.
- AC-2 -> test evidence: aggregate `source-self-fixture` output shows and passes the `closeout-reconciliation` step.
- AC-3 -> test evidence: focused `closeout-reconciliation` fixture passes while preserving existing fail-closed scenario assertions.
- AC-4 -> structural check: source surface choices still include unchanged `review-run` and `merge-gate`.
- AC-5 -> test evidence: generated skills parity passes.
- AC-6 -> manual evidence: changed files stay within allowed runtime/carrier/documentation scope and no release, package, workflow, #1279, #1280, or #1258 closeout files change.

## Minimal Path Applicability Records

- full-path-artifacts not_applicable rationale: #1278 is a bounded runtime fixture split with GitHub issue acceptance, focused source-surface checks, generated parity checks, and current Work Item carriers; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for this slice. consumer boundary: review, merge-ready, and closeout consume issue #1278, `.loom/work-items/WI-1278.md`, `.loom/progress/WI-1278.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, validation outputs, and hosted check readback. recheck condition: if scope expands into downstream Round 5 surfaces, release/package/workflow behavior, external host actions, or multi-module design beyond `loom_check.py` fixture surface selection, author the full suite before review.
