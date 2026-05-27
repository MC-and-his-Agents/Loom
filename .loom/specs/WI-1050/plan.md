# WI-1050 Plan

## Implementation Goal

Deliver scenario skill full/minimal suite path consumption boundaries for #1050 without redefining core contracts or implementing CLI behavior.

## Phases

### Phase 1

- Objective: Add a shared route matrix boundary for full/minimal suite path consumption.
- Deliverable: `src/skills/route-matrix.md`.
- Exit condition: route matrix maps `loom-story`, `loom-spec-review`, `loom-build`, `loom-pre-review`, and `loom-merge-ready` to their full/minimal path consumption responsibilities.

### Phase 2

- Objective: Update scenario skill input/output and completion contracts.
- Deliverable: `src/skills/loom-story/`, `src/skills/loom-spec-review/`, `src/skills/loom-build/`, `src/skills/loom-pre-review/`, `src/skills/loom-merge-ready/`.
- Exit condition: skills fail closed for full path missing inputs and only accept minimal path with valid `not_applicable` rationale, consumer boundary, and recheck condition.

### Phase 3

- Objective: Keep checked-in generated skill surface consistent.
- Deliverable: `skills/` regenerated from `src/skills`.
- Exit condition: `python3 tools/skills_surface.py check` passes.

## Constraints

- Architectural or governance constraints: scenario skills consume `spec-suite`, `evidence-map`, `consistency-analysis`, `gate-chain`, and GitHub task carrier profile contracts; they do not redefine those contracts.
- Workspace / rollout constraints: branch `work/1050-scenario-skills-full-minimal`.
- Purity or scope constraints: no #1052 CLI surface implementation; no #1051 drift-check ownership beyond generated surface consistency required by this PR.

## Validation

- Automated checks: `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; `python3 tools/check_release_surface.py`; `python3 tools/host_adapter_check.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`.
- Manual checks: `git diff --check`; focused `rg` checks for full/minimal suite path, scenario/acceptance mapping, `not_applicable` rationale, consumer boundary, recheck condition, and fail-closed boundaries.
- Runtime evidence: `.loom/progress/WI-1050.md`; `.loom/reviews/WI-1050.json`.
- Behavior evidence: source and generated skill surfaces expose the required consumption boundaries.
- Story scenario to evidence mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Fresh verification evidence: local validation and PR checks before merge.
- Execution ledger plan locator: `.loom/specs/WI-1050/plan.md`.
- Execution ledger validation evidence locator: `.loom/progress/WI-1050.md`.

## Test Strategy

- TDD or test-first expectation: documentation/skill contract change; use contract checks, generated-surface check, and focused grep.
- Regression coverage to add or preserve: preserve source contract checks, generated skills surface check, release surface check, host adapter check, version surface check, npm package check, and source `loom_check`.
- Cases that are intentionally not automated: qualitative review that wording consumes rather than redefines #1014-#1019.
- How failing tests or equivalent checks will be introduced before implementation: not_applicable; no executable behavior change.
- How passing tests or equivalent checks will be captured as test evidence: validation commands, review records, and PR checks.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence: not_applicable.

## Dependencies

- Blocking inputs: #1016 full/minimal suite, #1018 evidence-map and consistency-analysis, #1019 gate-chain consumption, #1049 GitHub task carrier profile.
- Required coordination: #1051 consumes source/generated drift-check closeout and #1036 deferred sync; #1052 remains CLI planning.
- Rollback boundary: revert this PR if scenario skills become the authority for core suite, evidence-map, consistency-analysis, gate-chain, or GitHub task carrier truth.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
