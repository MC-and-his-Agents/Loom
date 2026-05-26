# WI-1031 Spec

## Goal

Update the `loom-story` skill so Story Readiness and Story Business Confirmation clearly block or allow formal spec / plan shaping.

## Scope

- Align `loom-story` instructions with #1029 / #1030 verdict vocabulary: `confirmed`, `pending`, `revision-requested`, and `not_applicable`.
- State that `pending` and `revision-requested` fail closed before formal spec / plan consumption.
- Require `not_applicable` to carry a bypass rationale.
- Keep Story Business Confirmation limited to business semantics, not technical方案、测试策略、review、merge-ready 或代码质量。
- Regenerate checked-in skills runtime surfaces from `src/skills`.

## Out Of Scope

- Redefining the story intake authority contract; that is #1029.
- Changing the user-story scaffold; that is #1030.
- Updating spec-suite entry rules; that is #1032.
- Implementing full spec suite, task carrier, gate-chain, or CLI behavior.

## Key Scenarios

### Confirmed Story

Given Story Readiness and Story Business Confirmation are confirmed

When formal spec / plan shaping consumes the story

Then `loom-story` exposes the story as upstream semantics only and keeps Work Item, spec, plan, review, merge-ready, and closeout truth separate.

### Pending Or Revision Requested

Given Story Readiness or Business Confirmation is `pending` or `revision-requested`

When an agent tries to continue into formal spec / plan

Then `loom-story` tells the agent to stop, return to story shaping, or wait for user business confirmation.

### Not Applicable Story

Given the work has no business semantics to confirm

When story intake is marked `not_applicable`

Then `loom-story` requires a bypass rationale and downstream spec / plan may consume only that rationale.

## Acceptance Criteria

- `loom-story` no longer exposes `ready | needs-shaping | blocked | not-applicable` as Story Readiness decisions.
- `pending` and `revision-requested` block formal spec shaping in skill instructions and output contract references.
- `not_applicable` requires rationale in input and output references.
- Business Confirmation does not ask users to approve technical方案、测试策略、review 或代码质量。
- Source and generated skills surfaces stay synchronized.
