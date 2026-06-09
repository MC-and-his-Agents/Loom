# WI-1278 Spec

- Suite path: minimal

## Scenarios

- Scenario S1: `loom_check.py --profile source --source-surface closeout-reconciliation` runs closeout/reconciliation fixture checks under the stable `closeout-reconciliation` source-surface name.
- Scenario S2: `loom_check.py --profile source --source-surface source-self-fixture` preserves aggregate compatibility by running `review-run`, `merge-gate`, `closeout-reconciliation`, and the remaining source-self fixture steps.
- Scenario S3: generated skills runtime `loom_check.py` copies stay synchronized with canonical source while bootstrapped `.loom/bin` runtime copies remain manifest-aligned.

## Acceptance Criteria

- AC-1: The source surface choices expose `closeout-reconciliation`.
- AC-2: `source-self-fixture` includes `closeout-reconciliation` coverage.
- AC-3: Closeout/reconciliation fixture failures remain fail-closed and distinguishable by surface/category for closeout check/sync, reconciliation audit, reconciliation sync dry-run, status closeout payload checks, and synthetic closeout reconciliation payload samples.
- AC-4: Existing `review-run` and `merge-gate` source surface names and runner contract remain unchanged.
- AC-5: Generated skills parity passes after the surface split.
- AC-6: No release, package, workflow, #1279, #1280, or #1258 closeout behavior changes are introduced.

- Full suite artifacts not_applicable: rationale: #1278 is a bounded runtime fixture surface split with issue-authored acceptance and a minimal Work Item suite; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for review. consumer boundary: review, merge-ready, and closeout consume issue #1278, `.loom/work-items/WI-1278.md`, `.loom/progress/WI-1278.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, validation outputs, and hosted check readback. recheck condition: if #1278 expands beyond `loom_check.py` source-surface selection into downstream #1279/#1280 surfaces, release/package/workflow behavior, external host actions, or multi-module design beyond runner contract parity, author the full suite before review.
