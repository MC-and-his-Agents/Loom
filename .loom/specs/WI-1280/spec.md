# WI-1280 Spec

- Suite path: minimal

## Scenarios

- Scenario S1: `loom_check.py --profile source --source-surface installed-runtime` runs installed route, installed flow, runtime-state parity, bootstrapped embedded runtime, and install-layout dependent fixtures under the stable `installed-runtime` source-surface name.
- Scenario S2: `loom_check.py --profile source --source-surface source-self-fixture` preserves aggregate compatibility by including `review-run`, `merge-gate`, `closeout-reconciliation`, `retire-workspace`, `installed-runtime`, and the remaining source-self fixture steps.
- Scenario S3: generated skills runtime `loom_check.py` copies stay synchronized with canonical source while embedded and repo-local runtime compatibility remain intact.

## Acceptance Criteria

- AC-1: The source surface choices expose `installed-runtime`.
- AC-2: `source-self-fixture` includes `installed-runtime` coverage.
- AC-3: Installed runtime fixtures are diagnosable under `installed-runtime-fixture` and cover installed route/flow/runtime parity, bootstrapped embedded runtime behavior, and install-layout dependent fail-closed checks.
- AC-4: Existing `review-run`, `merge-gate`, `closeout-reconciliation`, `retire-workspace`, and aggregate `source-self-fixture` source surface names and runner contract remain unchanged.
- AC-5: Generated skills runtime copies stay aligned with canonical source.
- AC-6: No #1258 parent closeout, release, package, workflow, or user-visible runtime behavior changes are introduced.

- Full suite artifacts not_applicable: rationale: #1280 is a bounded runtime fixture surface split with issue-authored acceptance and a minimal Work Item suite; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for review. consumer boundary: review, merge-ready, and closeout consume issue #1280, `.loom/work-items/WI-1280.md`, `.loom/progress/WI-1280.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, validation outputs, and hosted check readback. recheck condition: if #1280 expands beyond `loom_check.py` source-surface selection into parent #1258 closeout, release/package/workflow behavior, external host actions, or multi-module runtime behavior beyond runner contract parity, author the full suite before review.
