# WI-1030 Spec

## Goal

Update the user-story scaffold so story intake exports scenario locators and Story Business Confirmation locators for formal spec / plan consumption.

## Scope

- Add stable scenario id and scenario locator fields to the user-story scaffold.
- Add a Business Confirmation locator field, while keeping `not_applicable` as a rationale-based bypass.
- State that `pending` and `revision-requested` stop formal spec / plan consumption at the story locator.
- Keep story output as upstream locator truth only; it must not copy delivery handoff, review, merge-ready, closeout, or formal spec / plan state.

## Out Of Scope

- Redefining the #1029 story intake authority contract.
- Updating `loom-story` routing behavior; that is #1031.
- Updating spec-suite entry rules; that is #1032.
- Adding task carrier or gate-chain behavior.

## Key Scenarios

### Confirmed Business Story

Given a story includes business-readable acceptance scenarios

When the story is confirmed for business semantics

Then it exposes scenario locators and a Business Confirmation locator for `spec.md` / `plan.md` to reference by locator.

### Pending Or Revision Requested

Given story readiness or business confirmation is still pending or revision-requested

When formal spec shaping starts

Then the scaffold tells the caller to stop at the story locator instead of copying or guessing story content.

### Not Applicable Story

Given the item has no business semantics to confirm

When story intake is marked `not_applicable`

Then the scaffold requires a rationale instead of manufacturing a Business Confirmation locator.

## Acceptance Criteria

- User-story scaffold includes scenario ids and scenario locators.
- User-story scaffold includes Business Confirmation locator or `not_applicable` rationale.
- Story scaffold explicitly avoids copying delivery handoff, review, merge-ready, closeout, or formal spec / plan state.
- Runtime checks cover the new locator fields.
