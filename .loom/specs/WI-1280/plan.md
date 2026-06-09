# WI-1280 Plan

- Suite path: minimal

## Implementation

- Phase 1: Add `SOURCE_SURFACE_INSTALLED_RUNTIME` and expose `installed-runtime` through existing `--source-surface` choices and profile contract anchors.
- Phase 2: Preserve aggregate behavior by making `source-self-fixture` include `installed-runtime` alongside `review-run`, `merge-gate`, `closeout-reconciliation`, `retire-workspace`, and remaining source-self fixture steps.
- Phase 3: Move installed route/flow/runtime-state, bootstrapped embedded runtime, installed pre-merge chain, and install-layout dependent checks out of the `merge-gate`/daily-execution-cli runner into a focused `installed-runtime` fixture runner while preserving fail-closed diagnostics.
- Phase 4: Synchronize generated skills runtime `loom_check.py` copies with canonical source, bind WI-1280 carriers and PR metadata to the current head, then stop for scheduler-owned gate.

## Deferred Items

- #1258 parent closeout remains deferred until all child issues close. Statement: deferred is not completed.
- Round 4, Round 6+, and Deferred roadmap work remain out of scope. Statement: deferred is not completed.
- Scheduler-owned semantic/spec review artifacts, guardian/loom_check gate consumption, controlled merge, post-merge readback, and closeout remain deferred to the scheduler. Statement: deferred is not completed.

## Validation

- S1 -> automated validation evidence: `python3 tools/loom_check.py --profile source --source-surface installed-runtime .`
- S2 -> automated validation evidence: `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- S3 -> automated validation evidence: `python3 tools/loom.py skills check --target . --json`
- AC-1 -> structural check: `python3 tools/loom_check.py --profile source --source-surface contract-only .` includes the `installed-runtime` profile contract anchor.
- AC-2 -> test evidence: aggregate `source-self-fixture` output shows and passes the `installed-runtime` step.
- AC-3 -> test evidence: focused `installed-runtime` fixture passes while preserving installed runtime fail-closed scenario assertions.
- AC-4 -> structural check: source surface choices still include unchanged `review-run`, `merge-gate`, `closeout-reconciliation`, `retire-workspace`, and `source-self-fixture`.
- AC-5 -> test evidence: generated skills parity passes.
- AC-6 -> manual evidence: changed files stay within allowed runtime/carrier scope and no release, package, workflow, #1258 closeout, or unrelated child implementation files change.

## Minimal Path Applicability Records

- full-path-artifacts not_applicable rationale: #1280 is a bounded runtime fixture split with GitHub issue acceptance, focused source-surface checks, generated parity checks, and current Work Item carriers; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for this slice. consumer boundary: review, merge-ready, and closeout consume issue #1280, `.loom/work-items/WI-1280.md`, `.loom/progress/WI-1280.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, validation outputs, and hosted check readback. recheck condition: if scope expands into parent #1258 closeout, release/package/workflow behavior, external host actions, or multi-module runtime behavior beyond `loom_check.py` fixture surface selection, author the full suite before review.
