# WI-1134 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1134 is a narrow gate integration slice that consumes already-implemented suite evidence and carrier validators from pre-review, implementation review, and merge-ready; consumer boundary: consistency-analysis implementation, closeout semantics, doctor/verify suite profile enforcement, and E2E governance regression remain later Work Items under #1136/#1145; recheck condition: this change expands into closeout behavior, new spec-kit-style commands, or full consistency-analysis authoring.

## Goal

Pre-review, implementation review, and merge-ready consume suite evidence and carrier validation before allowing downstream governance steps.

## Key Scenarios

### Scenario S1

Given a Work Item with suite evidence or carrier validation gaps
When `loom pre-review` or `loom gate pre-review` runs
Then the flow exposes `suite-evidence-validate` and `suite-carrier-validate` steps and blocks or falls back on blocking validator results.

### Scenario S2

Given an implementation review is recorded as `allow`
When `loom review record` writes the review record
Then it consumes suite evidence and carrier validation commands plus evidence-map and task-carrier locators in `consumed_inputs`.

### Scenario S3

Given merge-ready sees stale evidence or a carrier truth conflict
When `loom merge-ready` / `flow merge-ready` runs
Then the suite gate validation blocks before host merge without changing closeout semantics.

## Acceptance Criteria

- A1: `pre-review` output includes `suite_gate_validation`, `suite-evidence-validate`, and `suite-carrier-validate`.
- A2: implementation `review` flow includes the same suite gate validation payload.
- A3: `review record --decision allow` for implementation review fails closed unless suite evidence and carrier validation pass.
- A4: implementation review records store suite evidence/carrier validation commands and consumed evidence-map / task-carrier locators.
- A5: `merge-ready` output includes suite evidence/carrier gate steps and blocks stale evidence or carrier truth conflict through those validators.
- A6: CLI output is explicitly gate input evidence and does not replace Work Item, review record, merge-ready result, closeout evidence, or docs/source truth.
- A7: The implementation does not introduce `/speckit.*`, `.specify/`, or closeout semantic changes.
