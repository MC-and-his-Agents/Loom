# WI-1233 Spec

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1233 is a narrow diagnostics vocabulary implementation under a contract lane grant, scoped to active workspace diagnostics classification, focused fixture coverage, synchronized runtime copies, documentation, and WI-1233 carriers. It does not introduce a new cross-module architecture, external research track, host API contract, product workflow, or readiness workstream beyond issue #1233 acceptance criteria. consumer boundary: suite validate, spec review, implementation review, merge-ready, PR gate, hosted CI, and closeout may consume this locator only as the minimal formal suite path decision; current-head review, fact-chain/status readback, PR metadata/head binding, hosted checks, scheduler-owned review/gates, controlled merge, and closeout evidence remain required. recheck condition: require full-suite artifacts if this PR expands beyond #1233 diagnostics classification/source-runtime-test-doc-carrier scope, changes host mutation behavior, rewrites shared schema/parser/failure vocabulary outside `carrier_closeout_required`, alters release/package/workflow behavior, changes PR metadata schema, touches sibling/dependent issue implementation, or scheduler gates require full-suite evidence.

## Objective

Active workspace diagnostics must distinguish host-complete carrier drift from a true live shared-workspace conflict.

## Requirements

- When a candidate same-workspace Work Item has a non-terminal recovery checkpoint but readable GitHub host truth shows its issue is closed/completed or its PR is merged, diagnostics classify it as `carrier_closeout_required`.
- `carrier_closeout_required` is report-only, not a blocking live execution conflict.
- Remediation for `carrier_closeout_required` points to versioned carrier closeout sync and does not point to workspace retire.
- Existing `stale_carrier` behavior for terminal recovery carriers remains report-only.
- Existing `shared_workspace_conflict` behavior for live non-terminal same-workspace carriers remains blocking.
- Existing metadata/status boolean `closeout_required` semantics are not renamed or weakened.

## Non-Goals

- No broader schema/parser/failure vocabulary rewrite.
- No #1232, #1234, #1235, #1236, #1237, #1296, Round 10/11, release, merge, guardian, or live host configuration scope.
