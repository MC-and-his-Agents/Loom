# WI-862 Spec

## Outcome

Loom story intake exposes a lightweight user-owned business semantic confirmation point between Story Readiness and formal spec / plan consumption.

## Acceptance

- Story intake defines `Story Business Confirmation` as a separate artifact with schema marker `loom-story-business-confirmation/v1`.
- Confirmation decisions are limited to `pending`, `confirmed`, `revision-requested`, and `not-applicable`.
- Confirmation scope is limited to actor, capability, outcome, business value, acceptance scenarios, and out-of-scope boundaries.
- A user can confirm by replying `确认`; a user revision request returns the flow to story shaping instead of entering spec / plan.
- Pure governance, maintenance, formatting, link repair, and carrier-only changes can use `not-applicable` with a bypass rationale.
- Spec / plan / Work Item / gate references only consume confirmed or explicitly not-applicable story semantics.
- `loom-story` route and runtime contract summary expose the business confirmation contract.
- Story carrier checks fail closed when business confirmation is still `pending` or `revision-requested`.
- Generated `skills/` surface and `examples/new-project` runtime are refreshed from source.

## Non Goals

- Do not make users approve technical solutions, implementation details, test strategy, review quality, or code quality at this confirmation point.
- Do not turn story confirmation into a product database, product strategy approval, or universal requirement for pure maintenance work.
- Do not add HotCP-specific workflow fields to Loom core.
