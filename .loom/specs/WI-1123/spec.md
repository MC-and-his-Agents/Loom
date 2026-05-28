# WI-1123 Spec

## Goal

Prevent formal spec suites from reaching review when `plan.md` only summarizes `spec.md` instead of consuming scenario and acceptance locators mechanically.

## Scope

- Parse scenario ids and acceptance ids from `spec.md`.
- Require each parsed scenario id to appear in a `plan.md` validation strategy mapping.
- Require each parsed acceptance id to appear in a `plan.md` test strategy mapping.
- Report unexplained gaps as blocking `missing_spec_plan_mapping` findings on the `spec/plan` surface.
- Preserve read-only `loom suite validate` behavior.

## Non-Goals

- No final failure taxonomy expansion beyond the existing #1052 `missing_spec_plan_mapping` kind.
- No `flow spec-review` or `gate spec-review` integration.
- No evidence-map freshness, task carrier mapping, or closeout validation.
- No host, issue, PR, Project, review, merge-ready, or closeout writes from `loom suite validate`.
- No `/speckit.*` command names or `.specify/` layout.

## Acceptance Criteria

- AC-1123-1: Full path fixtures with scenario and acceptance mappings pass without mapping gaps.
- AC-1123-2: Full path fixtures with a missing scenario validation mapping block with `missing_spec_plan_mapping`.
- AC-1123-3: Full path fixtures with a missing acceptance test mapping block with `missing_spec_plan_mapping`.
- AC-1123-4: Mapping results are emitted under `payload.spec_plan_mapping` with required, mapped, and missing ids.
- AC-1123-5: Existing suite path, artifact, not_applicable, deferred, and advisory behavior remains read-only and unchanged.

## Guardrails

- CLI output remains evidence only; it does not replace Work Item truth, recovery truth, review records, merge-ready evidence, closeout evidence, or docs/source contracts.
- Deeper validation remains owned by #1124-#1125 and later FRs.
