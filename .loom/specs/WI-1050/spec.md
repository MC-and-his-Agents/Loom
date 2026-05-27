# WI-1050 Spec

## Goal

Update the scenario skills so the formal spec path consumers can distinguish full path and minimal path, fail closed when full path required artifacts are missing, and consume minimal path `not_applicable` rationale without redefining the core suite, evidence-map, consistency-analysis, or gate-chain contracts.

## Scope

- In scope:
  - `loom-story` story readiness and business confirmation boundary for suite path consumers.
  - `loom-spec-review` full/minimal suite path input and output consumption.
  - `loom-build` build readiness consumption of suite path and scenario/acceptance mappings.
  - `loom-pre-review` admission consumption of full path evidence and minimal path rationale.
  - `loom-merge-ready` merge gate consumption of reviewed suite evidence and minimal path rationale.
  - Route matrix and shared runtime reference text needed for scenario skills to consume the existing contracts.
- Out of scope:
  - Redefining #1014-#1019 core contracts.
  - Implementing #1052 CLI command surface planning.
  - Owning #1051 broader source/generated drift checks or #1036 source/generated sync closeout.

## Key Scenarios

### Scenario 1

Given
- a Work Item selects full formal spec path

When
- `loom-spec-review`, `loom-build`, `loom-pre-review`, or `loom-merge-ready` evaluates readiness

Then
- the skill consumes suite path locator, required artifact locators, provenance, evidence-map and consistency-analysis applicability, gate-chain status, and scenario/acceptance mapping freshness; missing required inputs fail closed with `block` or an explicit fallback.

### Scenario 2

Given
- a Work Item selects minimal formal spec path

When
- a scenario skill sees absent full path artifacts

Then
- the skill only treats the absence as valid when `not_applicable` includes rationale, consumer boundary, and recheck condition; unreasoned missing inputs, `deferred`, and source/generated sync backlog are not considered ready.

### Scenario 3

Given
- a pure governance or documentation Work Item has no product story semantics

When
- `loom-story` produces inputs for later `spec.md` and `plan.md`

Then
- it can provide `not_applicable` story readiness and business confirmation rationale, but it does not choose suite path or create evidence-map, consistency-analysis, review, merge-ready, or closeout truth.

## Behavior Evidence

- Story scenario mapping: not_applicable; this Work Item changes executable skill consumption boundaries, not product story semantics.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; pure governance skill-surface update.
- Scenario coverage: source and generated skill surfaces mention full path, minimal path, fail-closed behavior, `not_applicable` rationale, consumer boundary, recheck condition, and scenario/acceptance mapping consumption.
- Expected evidence locator: PR for #1050 and #1050 completion comment.
- Freshness rule: stale if source skill text, generated skill surface, or validation evidence no longer matches the PR head.
- Execution ledger acceptance locator: `.loom/specs/WI-1050/spec.md`.

## Exceptions And Boundaries

- Failure modes: a skill treats missing full path artifacts as ready, accepts `deferred` as `not_applicable`, or redefines suite/evidence/gate semantics instead of consuming existing contracts.
- Operational boundaries: generated `skills/` is refreshed from `src/skills` only to keep `tools/skills_surface.py check` green; #1051 remains responsible for broader source/generated sync closeout and #1036 consumption.
- Rollback or fallback expectations: revert this PR if scenario skills become authoritative over full/minimal suite, evidence-map, consistency-analysis, or gate-chain truth.

## Acceptance Criteria

- [x] Route matrix declares full/minimal suite path consumption rules for the five scenario skills.
- [x] `loom-story` states it produces story readiness/business confirmation inputs but does not choose suite path.
- [x] `loom-spec-review`, `loom-build`, `loom-pre-review`, and `loom-merge-ready` fail closed for missing full path required inputs.
- [x] Minimal path consumption requires `not_applicable` rationale, consumer boundary, and recheck condition.
- [x] Skills do not redefine #1014-#1019 core contracts or implement CLI surface.
- [x] Source and checked-in generated skill surfaces are consistent.
