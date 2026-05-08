# WI-576 Spec

## Goal

Define structured event evidence and fake orchestration fixtures so Loom can validate orchestration behavior without real model calls, real tool calls, or real tracker mutation.

## Acceptance Criteria

- The stable event schema is `loom-event-evidence/v1`.
- Event evidence includes item, session, attempt, event, source, subject, result, summary, observation, and provenance fields.
- Event evidence rejects copied authored truth fields such as `next_step`, `blockers`, `latest_validation_summary`, `recovery`, and `authored_truth`.
- `loom_check` validates missing required fields and forbidden authored truth fields.
- Fake agent fixtures cover success, failure, and tool failure.
- Fake tracker fixtures cover active, closed, and drift states.
- Tracker and agent fixtures do not call real hosts, real models, real tools, or schedulers.
- `make check` passes with no tracked verification drift.

## Non-Goals

- Do not introduce a scheduler state machine.
- Do not make event evidence a second truth source.
- Do not add `loom-build`; that belongs to #706.
- Do not add deterministic review engine behavior; that belongs to #675.
