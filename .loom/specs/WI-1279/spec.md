# WI-1279 Spec

- Suite path: minimal

## Scenarios

- Scenario S1: `loom_check.py --profile source --source-surface retire-workspace` runs retire, purity, and workspace cleanup fixtures under the stable `retire-workspace` source-surface name.
- Scenario S2: `loom_check.py --profile source --source-surface source-self-fixture` preserves aggregate compatibility by including `review-run`, `merge-gate`, `closeout-reconciliation`, `retire-workspace`, and the remaining source-self fixture steps.
- Scenario S3: generated skills runtime `loom_check.py` copies stay synchronized with canonical source while bootstrapped demo consumer runtime copies remain manifest-aligned.

## Acceptance Criteria

- AC-1: The source surface choices expose `retire-workspace`.
- AC-2: `source-self-fixture` includes `retire-workspace` coverage.
- AC-3: Retire/workspace fixture failures remain fail-closed and distinguishable by surface/category for purity-check diagnostics, workspace cleanup, workspace retire, dirty/non-Loom residue blocking, missing workspace locator, and missing install-layout negative coverage.
- AC-4: Existing `review-run`, `merge-gate`, `closeout-reconciliation`, and aggregate `source-self-fixture` source surface names and runner contract remain unchanged.
- AC-5: Generated skills runtime copies stay aligned with canonical source.
- AC-6: No #1280 installed-runtime, #1258 parent closeout, release, package, workflow, or user-visible lifecycle behavior changes are introduced.

- Full suite artifacts not_applicable: rationale: #1279 is a bounded runtime fixture surface split with issue-authored acceptance and a minimal Work Item suite; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for review. consumer boundary: review, merge-ready, and closeout consume issue #1279, `.loom/work-items/WI-1279.md`, `.loom/progress/WI-1279.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, validation outputs, and hosted check readback. recheck condition: if #1279 expands beyond `loom_check.py` source-surface selection into #1280 installed-runtime, parent closeout, release/package/workflow behavior, external host actions, or multi-module design beyond runner contract parity, author the full suite before review.
