# WI-1276 Spec

- Suite path: minimal

## Scenarios

- Scenario S1: `loom_check.py --profile source --source-surface review-run` runs the review-run fixture surface and reports failures under the stable `review-run-fixture` category.
- Scenario S2: `loom_check.py --profile source --source-surface source-self-fixture` preserves aggregate compatibility by running `review-run` plus the existing source-self fixture steps.
- Scenario S3: generated skills runtime `loom_check.py` copies stay synchronized with canonical source while bootstrapped `.loom/bin` runtime copies remain aligned with their manifests.

## Acceptance Criteria

- AC-1: The source surface choices expose `review-run`.
- AC-2: `source-self-fixture` includes `review-run` coverage.
- AC-3: Review-run fixtures preserve fake Codex, Codex App fallback/proof, schema drift, tracked edit, repeated blocker, profile, and local config assertions.
- AC-4: Generated skills parity passes after the surface split.
- AC-5: Root and demo bootstrapped runtime-state checks remain manifest-aligned.

- Full suite artifacts not_applicable: rationale: #1276 is a bounded runtime fixture split with issue-authored acceptance and a minimal Work Item suite; no separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact set is required for review. consumer boundary: review, merge-ready, and closeout consume issue #1276, `.loom/work-items/WI-1276.md`, `.loom/progress/WI-1276.md`, this minimal spec/plan, evidence-map, task-carrier, PR metadata, and validation outputs. recheck condition: if #1276 expands beyond review-run fixture surfacing into downstream #1277/#1278/#1279/#1280 surfaces, release/package/workflow behavior, or external host actions, author the full suite before review.
