# WI-706 Spec

## Acceptance

- `loom-build` is a first-class execution/build route between resume and pre-review.
- The route consumes Work Item, spec, plan, recovery baseline, validation baseline, workspace, and ownership constraints before claiming build readiness.
- Subagent-driven mode requires explicit task goal, context locators, read scope, write ownership, non-goals, validation expectation, output format, and integration target.
- Main execution remains responsible for integrating delegated output into implementation, validation evidence, recovery, status, and later review inputs.
- Unintegrated subagent output is a readiness blocker, not truth.
- Repeated blocker signals from delegated rounds are surfaced with root-cause escalation semantics.
- Overlapping write ownership fails closed or requires local integration before review/merge-ready.

## Non-Goals

- Do not implement a persistent worker daemon or queue lifecycle.
- Do not let subagent conclusions bypass Work Item, recovery, validation, review, or merge-ready carriers.
- Do not make broad parallel delegation the default when ownership boundaries overlap.
