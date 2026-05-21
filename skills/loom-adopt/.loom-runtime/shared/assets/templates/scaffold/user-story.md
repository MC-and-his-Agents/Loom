# Story Intake

本模板包含四个分离产物。`User Story` 是产品价值主体；`Story Readiness`、`Story Business Confirmation` 和 `Delivery Consumption Boundary` 是 intake 输出，不属于 User Story 主体。

## User Story

- Schema marker: loom-user-story/v1

- Actor:
- Capability:
- Outcome:
- Business value:
- Out of scope:

## Product Context

- Vision / roadmap locator:
- Host issue / notes locator:
- Discussion summary locator:

## Acceptance Scenarios

Use business-readable GWT. These scenarios describe desired behavior, not implementation steps or test scripts.

### Scenario 1

- Dimension: happy_path

Given
- a clear product or system starting point

When
- the actor uses the target capability

Then
- the intended outcome is observable

### Scenario 2

- Dimension:
- `not_applicable` rationale, if this dimension does not apply:

Given
- a relevant variant, risk, or boundary condition

When
- the actor or system reaches that condition

Then
- the outcome still stays within the intended story boundary

## Story Readiness

- Schema marker: loom-story-readiness/v1

- Decision: ready | needs-shaping | blocked | not-applicable
- Rationale:
- Story locator:
- Missing inputs:
- Bypass rationale, if not applicable:

## Story Business Confirmation

- Schema marker: loom-story-business-confirmation/v1

- Decision: pending | confirmed | revision-requested | not-applicable
- Confirmed by:
- Confirmation source:
- Revision request:
- Bypass rationale, if not applicable:
- Confirmation scope: actor, capability, outcome, business value, acceptance scenarios, out of scope.

## Delivery Consumption Boundary

- Schema marker: loom-story-delivery-mapping/v1

- Intended Work Item or FR:
- Spec entry expectation:
- Plan entry expectation:
- Story confirmation requirement: confirmed | not_applicable
- Story fields must not carry delivery handoff, recovery state, review findings, PR summary, merge-ready, or closeout state.
