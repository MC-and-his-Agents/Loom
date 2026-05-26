# WI-1029 Spec

## Goal

Strengthen the story intake contract so Loom treats story shaping as business semantic confirmation before formal spec / plan consumption, not as a second spec, plan, or execution state.

## Scope

- Define Story Readiness verdict vocabulary: `confirmed`, `pending`, `revision-requested`, `not_applicable`.
- Define Story Business Confirmation authority boundary and required fields.
- Keep User Story, Story Readiness, Story Business Confirmation, and Delivery Consumption Boundary separated.
- Keep story intake upstream of `spec.md` / `plan.md`; do not let it replace Work Item, recovery, review, merge-ready, or closeout truth.

## Out Of Scope

- Updating the user-story scaffold fields; that is #1030.
- Updating `loom-story` skill routing instructions; that is #1031.
- Updating spec-suite entry rules beyond the contract locator; that is #1032.
- Implementing full spec suite, task carrier, consistency analysis, gate-chain, or CLI automation.

## Key Scenarios

### Confirmed Story

Given a story has clear actor, capability, outcome, business value, acceptance scenarios, out-of-scope boundary, and provenance

When Story Readiness is recorded as `confirmed`

Then formal spec shaping may consume the story locator and scenario ids without copying the story into `spec.md`.

### Pending Story

Given a story lacks business confirmation or key semantic inputs

When Story Readiness or Story Business Confirmation is `pending`

Then formal spec shaping stops at story shaping and records the missing input instead of guessing the business semantics.

### Revision Requested

Given the user or reviewer requests a story change

When the decision is `revision-requested`

Then the flow returns to story shaping and does not continue into `spec.md` or `plan.md`.

### Not Applicable

Given the item is pure governance, maintenance, formatting, link repair, or carrier-only work

When story semantics do not apply

Then the flow records `not_applicable` with rationale and avoids manufacturing a fake story.

## Acceptance Criteria

- The authority contract uses the required readiness vocabulary.
- Runtime contract summary exposes the same vocabulary.
- Story carrier validation blocks `pending` / `revision-requested` before delivery consumption.
- Templates layer references the authority contract instead of duplicating a second truth source.
- Generated skill runtime surfaces stay synchronized.
