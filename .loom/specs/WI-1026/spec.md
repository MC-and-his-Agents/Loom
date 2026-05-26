# WI-1026 Spec

## Goal

Add a Loom-native PR slicing strategy that consumes #1024 delivery planning and #1025 issue-tree-plan output to decide when multiple Work Items may share one PR and when they must split.

## Scope

- In scope:
  - Methodology contract for PR slicing.
  - Scaffold template for PR slicing output.
  - README registration and repo-local fact chain carriers.
- Out of scope:
  - PR gate or merge-ready implementation (#1019).
  - GitHub Phase / FR / Work Item / Project mapping (#1027).
  - Skills routing (#1028).
  - Task carrier contracts (#1017).
  - CLI automation.

## Key Scenarios

### Scenario 1

Given
- an issue-tree plan lists multiple Work Items under the same FR

When
- an agent decides whether they can share one implementation PR

Then
- the PR slicing strategy records same-PR conditions, split-PR triggers, review risk, validation matrix, PR body linkage, merge-ready consumption, and closeout consumption.

### Scenario 2

Given
- one PR carries a primary Work Item and additional Work Item links

When
- review, merge-ready, and closeout consume the PR

Then
- each Work Item still has explicit evidence back to PR, head SHA, merge commit, validation, Project Status, and downstream state; PR body text alone is not treated as Loom truth.

## Behavior Evidence

- Story scenario mapping: not_applicable; this is a methodology/template contract.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Scenario coverage: contract sections and scaffold fields cover same-PR, split-PR, PR body, review, merge-ready, and closeout expectations.
- Expected evidence locator: PR #1082 and #1026 completion comment.
- Freshness rule: stale if issue-tree plan, Work Item scope, blocked-by/blocks, Project Status, PR head, or gate-chain multi-Work-Item support changes.
- Execution ledger acceptance locator: `.loom/specs/WI-1026/spec.md`.

## Exceptions And Boundaries

- Failure modes: strategy turns into a file-count heuristic, lets FRs directly carry implementation PRs, or lets PR body Markdown replace review/merge-ready/closeout truth.
- Operational boundaries: no PR gate, merge-ready, GitHub mapping, or CLI implementation is introduced by this Work Item.
- Rollback or fallback expectations: revert this PR if PR slicing duplicates execution truth or makes single PR multi-Work-Item evidence weaker than separate PRs.

## Acceptance Criteria

- [x] Contract defines same-PR conditions and split-PR triggers.
- [x] Contract defines primary Work Item and additional Work Item link handling.
- [x] Contract explains PR body, review evidence, merge-ready evidence, and closeout evidence relationships.
- [x] Contract states PR is a host carrier, not Loom completed truth.
- [x] Scaffold exposes fillable fields for slicing decision, review risk, validation matrix, merge-ready consumption, and closeout consumption.
- [x] Contract avoids implementing PR gate, merge-ready, GitHub mapping, skills routing, task carrier, or CLI logic.
