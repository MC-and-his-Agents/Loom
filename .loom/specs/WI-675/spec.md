# WI-675 Spec

## Goal

Make formal review execution deterministic by resolving and recording a stable review engine profile before `review run` invokes the Codex-backed reviewer.

## Acceptance Criteria

- The stable profile schema is `loom-review-engine-profile/v1`.
- The profile records adapter, engine, profile id, model, reasoning effort, timeout, context policy, selection reason, and override reason.
- `review run` passes explicit model and reasoning arguments to Codex instead of inheriting host defaults.
- Default, high-risk, spec-review, and repeated-blocker profile selection rules are documented.
- Manual profile, model, or reasoning overrides fail closed unless an override reason is recorded.
- Engine metadata includes the resolved profile for pass and fail-closed paths.
- `review_record_input` includes the resolved profile when engine review passes.
- Regression fixtures prove positive profile evidence, override evidence, missing-reason blocking, and missing profile contract failure.
- `make check` passes with no tracked verification drift.

## Non-Goals

- Do not turn Loom into a multi-engine marketplace.
- Do not add the review context pack or repeated blocker loop handling; that belongs to #679.
- Do not change authored review record truth semantics beyond evidence locators.
