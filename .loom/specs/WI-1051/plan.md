# WI-1051 Plan

## Implementation Goal

Deliver source/generated skills surface synchronization for #1051, including installed shared references and drift detection, without changing core contract semantics or CLI surface.

## Phases

### Phase 1

- Objective: Add docs-synced shared references to source skills.
- Deliverable: `src/skills/shared/references/...` copies for spec suite, linked scaffold templates, execution breakdown, task carrier, evidence-map, and consistency-analysis.
- Exit condition: source references match docs authority files.

### Phase 2

- Objective: Expose shared reference locators to installed skill consumers.
- Deliverable: route matrix, install layout, and relevant scenario skill text.
- Exit condition: installed skill surface can read the synchronized references for full/minimal path, task carrier, evidence-map, and consistency-analysis consumption.

### Phase 3

- Objective: Add drift detection and refresh generated surface.
- Deliverable: `tools/skills_surface.py` docs -> source reference sync check and regenerated `skills/`.
- Exit condition: `python3 tools/skills_surface.py check` passes and would fail on docs/source or source/generated drift.

### Phase 4

- Objective: Close out #1036 within #1051 evidence.
- Deliverable: #1051 closeout comment linking #1036 deferred handoff and PR evidence.
- Exit condition: #1036 is explicitly consumed or superseded by #1051 without reopening standalone work.

## Constraints

- Architectural or governance constraints: docs/source contracts remain authoritative; generated skills are an install surface.
- Workspace / rollout constraints: branch `work/1051-source-generated-skills-sync`.
- Purity or scope constraints: no #1052 CLI surface work; no #1014-#1019 core contract redefinition; no #1049/#1050 semantic rewrite.

## Validation

- Automated checks: `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; `python3 tools/check_release_surface.py`; `python3 tools/host_adapter_check.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`.
- Manual checks: `git diff --check`; focused `rg` checks for full suite, task carrier, evidence-map, consistency-analysis, source/generated, generated skills, drift, deferred, and not_applicable boundaries.
- Runtime evidence: `.loom/progress/WI-1051.md`; `.loom/reviews/WI-1051.json`.
- Behavior evidence: source references match docs authority and generated skills match source.
- Story scenario to evidence mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Fresh verification evidence: local validation and PR checks before merge.
- Execution ledger plan locator: `.loom/specs/WI-1051/plan.md`.
- Execution ledger validation evidence locator: `.loom/progress/WI-1051.md`.

## Test Strategy

- TDD or test-first expectation: documentation/skill surface contract change; use focused structural checks and generated-surface check.
- Regression coverage to add or preserve: preserve generated skills surface check and extend it to docs -> source reference drift.
- Cases that are intentionally not automated: qualitative review that wording consumes rather than redefines #1014-#1019.
- How failing tests or equivalent checks will be introduced before implementation: the new `skills_surface.py check` mapping would fail if any synced reference copy differs from docs authority.
- How passing tests or equivalent checks will be captured as test evidence: validation commands, review records, and PR checks.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence: not_applicable.

## Dependencies

- Blocking inputs: #1016 full/minimal suite and scaffold templates, #1017 execution breakdown/task carrier, #1018 evidence-map/consistency-analysis, #1019 gate-chain, #1049 GitHub task carrier profile, #1050 scenario skill routing.
- Required coordination: #1036 deferred source/generated sync need is consumed by this Work Item; #1052 remains out of scope.
- Rollback boundary: revert this PR if generated skills become the source of truth, if drift checks reject unchanged docs/source copies incorrectly, or if #1052 CLI scope enters this Work Item.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
