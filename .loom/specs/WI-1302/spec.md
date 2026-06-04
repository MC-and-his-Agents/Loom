# Spec

## Scenarios

### Scenario S1

Given a Work Item has a legal formal-suite NA path decision with rationale, consumer boundary, and recheck condition
When spec-review or PR gate consumes suite validation
Then the formal spec review gate may report the formal-suite NA result without requiring the full formal suite files.

### Scenario S2

Given a Work Item has a missing or invalid formal-suite NA rationale
When spec-review or PR gate consumes suite validation
Then the gate fails closed with the suite validation missing inputs.

### Scenario S3

Given a Work Item uses a formal-suite NA decision
When implementation review is evaluated
Then the implementation review artifact for the current head remains required.

## Acceptance Criteria

- AC-1: `suite validate` ready results include the legal formal-suite NA decision for spec-review consumption.
- AC-2: A legal formal-suite NA decision only makes formal spec review non-required.
- AC-3: Invalid formal-suite NA rationale still blocks.
- AC-4: Implementation review, fact-chain, CI, release/no-release, and closeout evidence are not bypassed.
