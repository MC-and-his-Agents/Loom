# WI-1122 Spec

## Goal

Prevent minimal or suite-level not_applicable paths from being treated as ready unless the bypass is authored and consumable.

## Scope

- Parse authored not_applicable and deferred records from existing suite artifacts.
- A valid not_applicable record must bind the artifact or suite scope and include rationale, consumer boundary, and recheck condition.
- Minimal suite readiness must cover full-path artifacts with valid not_applicable rationale.
- Suite-level not_applicable path must include valid suite-level rationale.
- Deferred records must not satisfy not_applicable readiness gaps.

## Non-Goals

- No spec.md to plan.md scenario or acceptance mapping validation.
- No final failure taxonomy expansion beyond #1052 failure kinds already consumed here.
- No `flow spec-review` or `gate spec-review` integration.
- No host, issue, PR, Project, review, merge-ready, or closeout writes from `loom suite validate`.
- No `/speckit.*` command names or `.specify/` layout.

## Acceptance Criteria

- AC-1122-1: Minimal path fixtures with valid full-suite not_applicable rationale pass.
- AC-1122-2: Minimal path fixtures with missing rationale, consumer boundary, recheck condition, or artifact binding block with `invalid_not_applicable_rationale`.
- AC-1122-3: Deferred-only records block with `deferred_as_completed` when they are consumed as a not_applicable readiness substitute.
- AC-1122-4: Suite-level not_applicable fixtures require valid suite-level rationale before returning `not_applicable`.
- AC-1122-5: Existing full path required artifact and advisory behavior remains read-only and does not mutate truth surfaces.

## Guardrails

- CLI output remains evidence only; it does not replace Work Item truth, recovery truth, review records, merge-ready evidence, closeout evidence, or docs/source contracts.
- Deeper validation remains owned by #1123-#1125.
