# WI-679 Implementation Contract

## In Scope

- `loom-review-context-pack/v1` evidence written by `review run`.
- Recent finding and disposition projection into review prompt input.
- Advisory `loom-repeated-blocker-signal/v1` evidence with source locators.
- Fixtures that prove repeated blockers recommend root-cause handling.

## Out Of Scope

- Hard merge gate enforcement for repeated blockers.
- New review truth carriers.
- New review engine selection behavior.
- Installed upgrade rehearsal or `loom-build`.

## Truth Boundary

The context pack and repeated blocker signal are input evidence. They must not replace the authored review record, Work Item, recovery entry, merge-ready evidence, closeout evidence, GitHub issue state, or PR state.
