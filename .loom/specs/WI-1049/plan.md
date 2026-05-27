# WI-1049 Plan

## Implementation Goal

Deliver the GitHub task carrier profile mapping for #1049 without updating scenario skills, generated surfaces, drift checks, or CLI behavior.

## Phases

### Phase 1

- Objective: Extend the GitHub profile contract.
- Deliverable: `docs/adoption/github-profile.md`.
- Exit condition: Contract covers carrier type, relationship, allowed use, locator/provenance, forbidden use, normalized status, and Project Status conflict handling.

### Phase 2

- Objective: Bind repo-local governance carriers.
- Deliverable: WI-1049 work item, progress, status, spec, plan, implementation contract, and review record.
- Exit condition: PR gate consumes WI-1049 instead of stale retained carriers.

## Constraints

- Architectural or governance constraints: GitHub task carriers are host-backed mirrors or unit carriers; Loom truth remains in Work Item, recovery, review, merge-ready, closeout, evidence-map, and consistency-analysis.
- Workspace / rollout constraints: branch `work/1049-github-task-carrier-profile`.
- Purity or scope constraints: do not edit scenario `SKILL.md`, route matrices, source/generated shared references, installer checks, or CLI command surfaces in this Work Item.

## Validation

- Automated checks: `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Manual checks: `git diff --check`; focused `rg` checks from #1049.
- Runtime evidence: `.loom/progress/WI-1049.md`; `.loom/reviews/WI-1049.json`.
- Behavior evidence: GitHub profile contract contains required carrier mappings and forbidden-use statements.
- Story scenario to evidence mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Fresh verification evidence: local validation and PR checks before merge.
- Execution ledger plan locator: `.loom/specs/WI-1049/plan.md`.
- Execution ledger validation evidence locator: `.loom/progress/WI-1049.md`.

## Test Strategy

- TDD or test-first expectation: documentation/profile-only change; use contract checks and focused grep.
- Regression coverage to add or preserve: preserve source contract checks and skills surface check.
- Cases that are intentionally not automated: qualitative judgment for unusual external tracker mappings.
- How failing tests or equivalent checks will be introduced before implementation: not_applicable; no executable behavior changes.
- How passing tests or equivalent checks will be captured as test evidence: validation commands and review records.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence: not_applicable.

## Dependencies

- Blocking inputs: #1017 task carrier contract and #1027 GitHub host mapping.
- Required coordination: #1050 consumes this profile for scenario skills; #1051 consumes source/generated synchronization and #1036 deferred sync.
- Rollback boundary: revert this PR if GitHub carriers become authoritative over Work Item, evidence, review, merge-ready, or closeout truth.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
