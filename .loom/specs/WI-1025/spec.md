# WI-1025 Spec

## Goal

Add a Loom-native issue-tree-plan template that consumes the #1024 delivery planning contract and expresses the planned Phase / FR / Work Item tree before execution begins.

## Scope

- In scope:
  - Methodology contract for issue-tree planning.
  - Scaffold template for issue-tree-plan output.
  - README registration and repo-local fact chain carriers.
- Out of scope:
  - PR slicing strategy (#1026).
  - GitHub Phase / FR / Work Item / Project mapping (#1027).
  - Skills routing (#1028).
  - Task carrier contracts (#1017).
  - Gate-chain or CLI automation.

## Key Scenarios

### Scenario 1

Given
- a delivery planning result says a target needs Phase / FR / Work Item decomposition

When
- an agent creates an issue-tree plan

Then
- the plan records phase boundary, FR list, Work Item list, dependencies, deferred/not_applicable decisions, and host carrier mapping.

### Scenario 2

Given
- an issue-tree plan references GitHub Project, checklist, tasks.md, or another host carrier

When
- review, merge-ready, or closeout consumes the plan

Then
- those host carriers are treated as organization or task-carrier surfaces only and do not replace Work Item, recovery, review, merge-ready, or closeout truth.

## Behavior Evidence

- Story scenario mapping: not_applicable; this is a methodology/template contract.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Scenario coverage: contract sections and scaffold fields cover the expected planning outputs and forbidden uses.
- Expected evidence locator: PR pending and #1025 completion comment.
- Freshness rule: stale if issue-tree-plan output no longer matches delivery planning, parent/sub-issue relations, blocked-by/blocks, Project status, or PR slicing decisions.
- Execution ledger acceptance locator: `.loom/specs/WI-1025/spec.md`.

## Exceptions And Boundaries

- Failure modes: template becomes a progress tracker, review record, or Project-status replacement.
- Operational boundaries: no GitHub mutation or CLI implementation is introduced by this Work Item.
- Rollback or fallback expectations: revert this PR if issue-tree plan is judged to duplicate execution truth or hard-code current #1012 issue numbers as Loom defaults.

## Acceptance Criteria

- [x] Template includes phase boundary, FR list, Work Item list, dependencies, deferred/not_applicable, and host carrier mapping.
- [x] Template can express blocked-by / blocks planning relations.
- [x] Template states it does not carry execution progress, review verdict, merge-ready, or closeout.
- [x] Template can be consumed by PR slicing and GitHub mapping.
- [x] Template avoids hard-coding current issue numbers as Loom defaults.
