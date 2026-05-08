# WI-675 Implementation Contract

## In Scope

- Review engine profile schema and deterministic profile selection.
- Explicit Codex `--model` and reasoning configuration for `review run`.
- Evidence fields under `engine.profile`, engine metadata, and `review_record_input.engine_profile`.
- Fail-closed override semantics requiring an override reason.
- Mechanical fixtures in `loom_check`.

## Out Of Scope

- Multiple review engines.
- Repo-specific review instruction expansion.
- Repeated blocker context-pack construction.
- Release publication or v0.8.0 final closeout.

## Truth Boundary

The resolved profile is review execution evidence. It does not replace the authored review record, Work Item, recovery entry, merge-ready evidence, closeout evidence, GitHub issue state, or PR state.
