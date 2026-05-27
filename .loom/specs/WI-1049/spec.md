# WI-1049 Spec

## Goal

Define the GitHub task carrier profile mapping so GitHub issue, sub-issue, Project item, checklist, repo-local `tasks.md`, external tracker, and `not_applicable` carriers can carry execution breakdown status without replacing Loom truth.

## Scope

- In scope:
  - GitHub task carrier profile table in `docs/adoption/github-profile.md`.
  - Locator / provenance requirements for each carrier type.
  - Normalized status rules for `pending`, `in_progress`, `done`, `blocked`, `deferred`, and `not_applicable`.
  - Project `Status` conflict handling for host agents.
- Out of scope:
  - Scenario skills routing (#1050).
  - Source/generated skills surface synchronization (#1051).
  - Drift check implementation.
  - CLI command surface (#1052).
  - Redefining #1014-#1019 core contracts.

## Key Scenarios

### Scenario 1

Given
- an execution breakdown unit is represented by a GitHub sub-issue, Project item, checklist item, repo-local task row, external tracker link, or explicit `not_applicable` rationale

When
- an agent reads that carrier through the GitHub profile

Then
- the carrier exposes type, relationship, locator, provenance, normalized status, and forbidden-use boundaries without becoming the Work Item, recovery, review, merge-ready, closeout, behavior evidence, or test evidence truth.

### Scenario 2

Given
- GitHub workflow or user action moves a Project item to `Done`

When
- an agent evaluates #1049 or later Work Item completion

Then
- it must verify issue, PR, merge commit, recovery, review, merge-ready, closeout, and evidence freshness before treating the status as consumable.

## Behavior Evidence

- Story scenario mapping: not_applicable; this is a host profile mapping contract.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Scenario coverage: `docs/adoption/github-profile.md` includes the GitHub task carrier profile table, normalized status rules, and host-agent Project Status reconciliation rule.
- Expected evidence locator: PR #1103 and #1049 completion comment.
- Freshness rule: stale if Project Status, issue state, PR state, review, merge-ready, closeout, or evidence-map freshness conflicts with Loom truth carriers.
- Execution ledger acceptance locator: `.loom/specs/WI-1049/spec.md`.

## Exceptions And Boundaries

- Failure modes: Project `Done`, checklist checked, issue closed, PR merged, or external tracker `Done` is treated as completed truth.
- Operational boundaries: no scenario skill routing, source/generated surface sync, drift implementation, GitHub automation, or CLI command surface is introduced by this Work Item.
- Rollback or fallback expectations: revert this PR if GitHub carrier state becomes authoritative over Work Item, evidence, review, merge-ready, or closeout truth.

## Acceptance Criteria

- [x] GitHub task carrier profile covers Work Item issue, non-Work-Item sub-issue, Project item, checklist item, repo-local `tasks.md`, external tracker, and `not_applicable`.
- [x] Each carrier row declares allowed use, locator / provenance, and forbidden use.
- [x] Carrier states normalize to the task carrier vocabulary from #1017.
- [x] Project `Status` remains a host view field, not completed truth.
- [x] Host agent guidance requires reconciliation against Work Item, PR, merge commit, recovery, review, merge-ready, closeout, and evidence freshness.
