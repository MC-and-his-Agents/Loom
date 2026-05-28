# WI-1141 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1141 is a narrow review record consumption slice that records locators already consumed by existing suite CLI gates; it does not introduce consistency analyze execution or a new full suite artifact type; consumer boundary: consistency analyze implementation and E2E governance fixtures remain later Work Items under #1136/#1145; recheck condition: review starts deriving suite truth, writing parallel review records, or consuming consistency-analysis findings as authority.

## Goal

`loom-review` records which suite, evidence-map, task-carrier, and consistency-analysis locators it consumed when writing the single authored review record.

## Scope

- In scope: review record `consumed_inputs`, suite gate consumed locator payloads, source/generated runtime sync, CLI contract assertions, and #1141 Loom carriers.
- Out of scope: implementing `loom suite consistency analyze`, creating parallel review records, changing review authority, GitHub host writes beyond normal PR/closeout flow, `/speckit.*`, and `.specify/`.

## Key Scenarios

### Scenario S1

Given a spec review records an `allow` decision
When the suite validation CLI JSON passes
Then the review record preserves the consumed suite validation command and suite artifact locators.

### Scenario S2

Given an implementation review records an `allow` decision
When suite evidence and carrier validations pass
Then the review record preserves evidence-map, task-carrier, and consistency-analysis locator fields in `consumed_inputs`.

### Scenario S3

Given review record evidence is later consumed by review gate, merge-ready, or closeout
When those gates read the record
Then the authored review decision remains the only review authority and consumed CLI locators remain evidence-only.

## Acceptance Criteria

- A1: Spec review records include `suite_validation`, `suite_spec`, `suite_plan`, `suite_evidence_map`, `suite_consistency_analysis`, and `suite_task_carriers` under `consumed_inputs`.
- A2: Implementation review records include `suite_evidence_validation`, `suite_carrier_validation`, `suite_evidence_map`, `suite_consistency_analysis`, and `suite_task_carriers` under `consumed_inputs`.
- A3: Consumed locators do not replace Work Item truth, review authority, merge-ready evidence, closeout evidence, docs/source truth, or Project state.
- A4: CLI contract checks cover the review record consumption payload.
- A5: Source/generated runtime copies remain synchronized.
