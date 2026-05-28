# WI-1125 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1125 is a narrow CLI integration slice that only needs spec, plan, implementation contract, generated runtime, docs, and regression checks; consumer boundary: suite evidence, carrier, merge-ready, closeout, and E2E governance consumers remain owned by #1126, #1136, and #1145; recheck condition: #1126 starts evidence/carrier/merge-ready validation or this change expands beyond spec-review integration.

## Goal

Spec-review flow and gate consumers must fail closed on incomplete or invalid formal suite readiness by consuming `loom suite validate` before spec review approval is allowed.

## Key Scenarios

### Scenario S1

Given a Work Item with an incomplete formal spec suite
When `flow spec-review` runs
Then the flow consumes suite validation output and blocks instead of preparing approval.

### Scenario S2

Given a spec review record request with decision `allow`
When suite validation reports blocking gaps
Then the review record command blocks and exposes the suite validation evidence.

## Acceptance Criteria

- [ ] A1: `flow spec-review` includes a `suite-validate` step and exposes suite validation output.
- [ ] A2: `gate spec-review` continues to delegate to the spec-review flow and inherits suite validation blocking behavior.
- [ ] A3: Recording `allow` for `kind=spec_review` blocks when suite validation does not pass.
- [ ] A4: The installed-skill regression fixture covers incomplete formal suite blocking approval.
