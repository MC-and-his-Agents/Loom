# WI-1277 Spec

- Suite path: minimal

## Scenarios

- Scenario S1: `loom_check.py --profile source --source-surface merge-gate` runs the existing source-self merge/PR/merge-ready gate fixture surface under the stable `merge-gate` source-surface name.
- Scenario S2: `loom_check.py --profile source --source-surface source-self-fixture` preserves aggregate compatibility by running `review-run`, `merge-gate`, and the remaining source-self fixture steps.
- Scenario S3: generated skills runtime `loom_check.py` copies stay synchronized with canonical source while bootstrapped `.loom/bin` runtime copies remain manifest-aligned.

## Acceptance Criteria

- AC-1: The source surface choices expose `merge-gate`.
- AC-2: `source-self-fixture` includes `merge-gate` coverage.
- AC-3: Merge-gate fixture failures remain fail-closed and distinguishable by surface `merge-gate` and scenario messages for controlled merge, PR gate, merge-ready, checkpoint merge, stale review, CI bypass, required gate, retained result, and ruleset coverage.
- AC-4: Generated skills parity passes after the surface split.
- AC-5: No release, package, workflow, #1278, #1279, #1280, or #1258 closeout behavior changes are introduced.

- Full suite artifacts not_applicable: rationale: #1277 is a bounded runtime fixture surface split with issue-authored acceptance and a minimal Work Item suite; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for review. consumer boundary: review, merge-ready, and closeout consume issue #1277, `.loom/work-items/WI-1277.md`, `.loom/progress/WI-1277.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, validation outputs, and hosted check readback. recheck condition: if #1277 expands beyond `loom_check.py` source-surface selection into downstream #1278/#1279/#1280 surfaces, release/package/workflow behavior, external host actions, or multi-module design beyond runner contract parity, author the full suite before review.
