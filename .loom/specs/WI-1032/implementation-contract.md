# WI-1032 Implementation Contract

This WI owns the spec-suite entrance wording that consumes Story Readiness and Story Business Confirmation before formal `spec.md` / `plan.md` shaping.

## Owned Changes

- `docs/methodology/templates/spec-suite.md`
- `docs/methodology/templates/scaffold/spec.md`
- `docs/methodology/templates/scaffold/plan.md`
- `docs/methodology/templates/scaffold/full-suite-index.md`
- WI-1032 Loom carriers under `.loom/`
- `.loom/progress/WI-1031.md` only to terminalize the inherited closed carrier after #1031 merge/closeout

## Contract Rules

- Story Readiness and Story Business Confirmation are separate consumed states.
- `confirmed` and rationale-backed `not_applicable` are the only states that allow story semantics to enter formal spec shaping.
- `pending` and `revision-requested` fail closed and may only be recorded as blocking locators.
- `spec.md` and `plan.md` consume story locators and scenario ids; they do not copy the User Story as a second truth source.
- `not_applicable` must include rationale, consumer boundary, and recheck condition.

## Non-Goals

- No story intake contract rewrite.
- No gate-chain implementation.
- No generated runtime surface update unless required by source validation.
