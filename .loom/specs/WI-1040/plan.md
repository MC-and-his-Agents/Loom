# WI-1040 Plan

## Implementation Goal

Finish the #1017 task carrier replacement boundary by documenting how `tasks.md`, GitHub issue/sub-issue, Project item, checklist, external tracker, and `not_applicable` relate to execution breakdown units without replacing `Work Item` or evidence truth.

## Phases

### Phase 1

- Objective: Define task carrier replacement semantics.
- Deliverable: `docs/methodology/harness/task-carrier-contract.md`.
- Exit condition: Contract covers optional `tasks.md`, GitHub/Project/checklist/external tracker carrier semantics, status mapping, locator/provenance, and forbidden uses.

### Phase 2

- Objective: Connect GitHub profile and issue-tree planning boundaries.
- Deliverable: Updates to `docs/adoption/github-profile.md` and `docs/methodology/templates/issue-tree-plan.md`.
- Exit condition: GitHub carrier mapping can be consumed without treating Project/checklist/task state as truth.

### Phase 3

- Objective: Bind repo-local execution evidence.
- Deliverable: `.loom/work-items/WI-1037.md` through `.loom/work-items/WI-1040.md`, `.loom/progress/WI-1037.md` through `.loom/progress/WI-1040.md`, `.loom/specs/WI-1040/*`, and review records.
- Exit condition: Current fact chain points to `WI-1040`, prior checkpoints are terminal, build checkpoint can pass, and PR #1090 consumes the evidence.

## Constraints

- Do not modify `skills/route-matrix.md`, `src/skills/route-matrix.md`, scenario `SKILL.md`, or generated skills runtime surface.
- Do not implement #1018 evidence-map, #1019 gate-chain, #1020 skills/GitHub profile integration, or CLI automation.
- Consume #1016 only through stable main-branch minimal/full boundary; do not depend on unmerged #1016 template details.

## Validation

- Automated checks:
  - `git diff --check`
  - focused `rg` for `tasks.md`, Project done, task done, behavior evidence, test evidence, task carrier, locator, provenance, and Work Item truth boundaries
  - `python3 tools/skills_surface.py check`
  - `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Manual checks:
  - Confirm no route matrix, scenario skill, generated runtime, evidence-map, gate-chain, or CLI surface was changed.
- Runtime evidence:
  - `.loom/progress/WI-1040.md`
- Behavior evidence:
  - `docs/methodology/harness/task-carrier-contract.md`
  - `docs/adoption/github-profile.md`
- Story scenario to evidence mapping:
  - `not_applicable`
- Story business confirmation locator or `not_applicable` rationale:
  - `not_applicable`
- Fresh verification evidence:
  - Local validation summaries and PR #1090 checks.
- Execution ledger plan locator:
  - `.loom/specs/WI-1040/plan.md`
- Execution ledger validation evidence locator:
  - `.loom/progress/WI-1040.md`

## Test Strategy

- TDD or test-first expectation:
  - `not_applicable`; this is a methodology contract change.
- Regression coverage to add or preserve:
  - Preserve `skills_surface` no-drift check and `loom_check` contract-only source surface.
- Cases that are intentionally not automated:
  - GitHub Project automation and generated skills synchronization, deferred to #1020.
- How failing tests or equivalent checks will be introduced before implementation:
  - `not_applicable`; validation is structure and contract consistency.
- How passing tests or equivalent checks will be captured as test evidence:
  - `.loom/progress/WI-1040.md`, review records, and PR checks.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence:
  - `not_applicable`.

## Subagent Output Integration

- Owned outputs:
  - Read-only explorer summaries for existing truth boundaries and GitHub issue inputs.
- Integration owner:
  - main agent.
- Required evidence from each subagent:
  - Concise findings with file and issue locators.
- Review or reconciliation needed before merge-ready:
  - Main agent reconciles explorer findings into contract docs and repo-local carriers.
- Handoff notes locator, or `not_applicable`:
  - #1020 integration requirement in `docs/methodology/harness/task-carrier-contract.md`.

## Dependencies

- Blocking inputs:
  - #1014 / #1027 completed contracts.
  - #1016 stable minimal/full boundary on main.
  - #1037-#1039 local checkpoint outputs.
- Required coordination:
  - #1018 consumes locators.
  - #1020 consumes skills/GitHub profile integration needs.
- Rollback boundary:
  - Revert PR #1090 contract docs and `.loom` carriers if the task carrier boundary needs to be withdrawn.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
