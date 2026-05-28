# WI-1131 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1131 is a narrow CLI validation slice for carrier inspect/validate and only needs spec, plan, implementation contract, evidence-map, execution-breakdown, task-carrier, docs, and CLI contract fixtures; consumer boundary: Project/checklist host reconciliation, pre-review/review/merge-ready integration, closeout reconciliation, consistency-analysis, E2E governance, and doctor/verify integration remain owned by later Work Items under #1126/#1136/#1145; recheck condition: this change expands beyond carrier inspect/validate or a later consumer requires the full suite path.

## Goal

`loom suite carrier inspect` and `loom suite carrier validate` expose task carrier state without allowing carrier state to replace Loom truth.

## Key Scenarios

### Scenario S1

Given a task-carrier table with supported carrier types
When carrier inspect runs
Then it reports carrier locators, normalized statuses, relationships, Work Item backlinks, and consumed contracts.

### Scenario S2

Given a task-carrier row with missing or invalid locator, status, relationship, or Work Item backlink
When carrier validate runs
Then it blocks with `missing_task_carrier_locator`.

### Scenario S3

Given a carrier row that claims Project Done, checklist checked, carrier done, or deferred state satisfies Work Item/evidence/review/merge-ready/closeout truth
When carrier validate runs
Then it blocks with `carrier_truth_conflict` or `deferred_as_completed`.

## Acceptance Criteria

- A1: `suite carrier inspect` remains read-only and emits the shared JSON envelope.
- A2: Inspect output includes recognized carrier types, normalized status vocabulary, relationship vocabulary, rows, locators, Work Item truth locators, and consumed contracts.
- A3: `suite carrier validate` remains read-only and blocks missing task-carrier locators or incomplete required fields.
- A4: Unknown carrier type, normalized status, or relationship values block.
- A5: Missing Work Item backlink or multiple primary carriers for one breakdown unit block.
- A6: Carrier done, Project Done, checklist checked, and deferred-as-completed cannot satisfy Work Item, evidence, review, merge-ready, or closeout truth.
- A7: The implementation does not introduce `/speckit.*`, `.specify/`, host writes, review writes, merge-ready writes, or closeout writes.
