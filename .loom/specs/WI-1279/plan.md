# WI-1279 Plan

- Suite path: minimal

## Implementation

- Phase 1: Add `SOURCE_SURFACE_RETIRE_WORKSPACE` and expose `retire-workspace` through existing `--source-surface` choices and profile contract anchors.
- Phase 2: Preserve aggregate behavior by making `source-self-fixture` include `retire-workspace` alongside `review-run`, `merge-gate`, `closeout-reconciliation`, and remaining source-self fixture steps.
- Phase 3: Move repo-local retire/workspace/purity cleanup fixtures out of `merge-gate` into a focused `retire-workspace` fixture runner while preserving fail-closed diagnostics.
- Phase 4: Add local dirty/non-Loom residue and missing install-layout negative coverage to the focused `retire-workspace` fixture without creating the #1280 installed-runtime surface.
- Phase 5: Synchronize generated skills runtime `loom_check.py` copies with canonical source, bind WI-1279 carriers and PR metadata to the current head, then stop for scheduler-owned gate.

## Deferred Items

- #1280 installed-runtime fixtures remain deferred until #1279 merge/readback. Statement: deferred is not completed.
- #1258 parent closeout remains deferred until all child issues close. Statement: deferred is not completed.
- Round 4, Round 6+, and Deferred roadmap work remain out of scope. Statement: deferred is not completed.

## Validation

- S1 -> automated validation evidence: `python3 tools/loom_check.py --profile source --source-surface retire-workspace .`
- S2 -> automated validation evidence: `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- S3 -> automated validation evidence: `python3 tools/loom.py skills check --target . --json`
- AC-1 -> structural check: `python3 tools/loom_check.py --profile source --source-surface contract-only .` includes the `retire-workspace` profile contract anchor.
- AC-2 -> test evidence: aggregate `source-self-fixture` output shows and passes the `retire-workspace` step.
- AC-3 -> test evidence: focused `retire-workspace` fixture passes while preserving fail-closed scenario assertions.
- AC-4 -> structural check: source surface choices still include unchanged `review-run`, `merge-gate`, `closeout-reconciliation`, and `source-self-fixture`.
- AC-5 -> test evidence: generated skills parity passes.
- AC-6 -> manual evidence: changed files stay within allowed runtime/carrier scope and no release, package, workflow, #1280, or #1258 closeout files change.

## Minimal Path Applicability Records

- full-path-artifacts not_applicable rationale: #1279 is a bounded runtime fixture split with GitHub issue acceptance, focused source-surface checks, generated parity checks, and current Work Item carriers; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for this slice. consumer boundary: review, merge-ready, and closeout consume issue #1279, `.loom/work-items/WI-1279.md`, `.loom/progress/WI-1279.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, validation outputs, and hosted check readback. recheck condition: if scope expands into downstream #1280 installed-runtime, release/package/workflow behavior, external host actions, or multi-module design beyond `loom_check.py` fixture surface selection, author the full suite before review.
