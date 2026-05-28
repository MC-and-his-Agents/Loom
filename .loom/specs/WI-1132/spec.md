# WI-1132 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1132 is a narrow carrier-validation slice that deepens existing `suite carrier validate` behavior and only needs spec, plan, implementation contract, evidence-map, execution-breakdown, task-carrier, docs, and CLI contract fixtures; consumer boundary: pre-review/review/merge-ready integration, closeout reconciliation, consistency-analysis, E2E governance, and doctor/verify integration remain owned by later Work Items under #1126/#1136/#1145; recheck condition: this change expands beyond carrier host signal classification or a later consumer requires the full suite path.

## Goal

`loom suite carrier validate` detects host mirror conflicts between carrier, Work Item, Project, checklist, issue, and PR signals before merge-ready.

## Key Scenarios

### Scenario S1

Given a task-carrier row with Project Done and issue open host mirror signals
When carrier validate runs
Then it blocks with `carrier_truth_conflict` and reports a stable Project/issue conflict classification.

### Scenario S2

Given a checklist carrier row that says checked while evidence is missing
When carrier validate runs
Then it blocks with `carrier_truth_conflict` without treating checklist checked as evidence.

### Scenario S3

Given a PR merged host signal while the issue mirror is still open
When carrier validate runs
Then it blocks with `carrier_truth_conflict` and keeps PR merged as merge locator evidence only.

## Acceptance Criteria

- A1: Carrier inspect exposes the recognized host truth signal vocabulary.
- A2: Carrier validate remains read-only and emits `truth_signal_classifications` and `host_signal_conflicts`.
- A3: Project Done with issue open blocks with `carrier_truth_conflict`.
- A4: Checklist checked with evidence missing blocks with `carrier_truth_conflict`.
- A5: PR merged with issue open blocks with `carrier_truth_conflict`.
- A6: Existing #1131 carrier locator, status, relationship, primary uniqueness, deferred-as-completed, and truth replacement fixtures still pass.
- A7: The implementation does not introduce host writes, auto-sync, pre-review/review/merge-ready integration, closeout semantic changes, `/speckit.*`, or `.specify/` surfaces.
