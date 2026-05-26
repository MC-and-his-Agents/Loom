# WI-1027 Spec

## Goal

Define the GitHub profile mapping that lets Loom consume delivery planning output as host-backed `Phase / FR / Work Item / Project / PR` carriers without letting GitHub objects replace Loom truth.

## Scope

- In scope:
  - GitHub profile contract for Phase, FR, Work Item, Project item, and implementation PR.
  - Authority boundary, locator/provenance, and forbidden-use rules for each host object.
  - Project `Status` semantics for `Todo`, `In Progress`, and `Done`.
  - Native parent/sub-issue and `blocked-by/blocks` synchronization rules.
  - Synchronized reference surfaces.
- Out of scope:
  - GitHub API automation.
  - Skills routing (#1028).
  - Task carrier contracts (#1017).
  - Gate-chain implementation (#1019).
  - CLI automation (#1052).

## Key Scenarios

### Scenario 1

Given
- delivery planning produces a Phase with FR and Work Item children

When
- Loom maps the plan into GitHub

Then
- Phase, FR, and Work Item hierarchy is represented with native parent/sub-issue relationships, while execution dependencies are represented with native `blocked-by/blocks`.

### Scenario 2

Given
- a GitHub Project item moves to `Done`

When
- an agent evaluates completion

Then
- it must still verify issue state, PR, Work Item, recovery, review, merge-ready, merge commit, and closeout evidence before treating the item as completed.

## Behavior Evidence

- Story scenario mapping: not_applicable; this is a host profile mapping contract.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Scenario coverage: GitHub profile sections define host object boundaries, hierarchy/dependency mapping, Project Status semantics, and drift handling.
- Expected evidence locator: PR for #1027 and #1027 completion comment.
- Freshness rule: stale if GitHub parent/sub-issue, blocked-by/blocks, Project Status, issue state, PR state, or closeout evidence conflicts with Loom carriers.
- Execution ledger acceptance locator: `.loom/specs/WI-1027/spec.md`.

## Exceptions And Boundaries

- Failure modes: Project Status becomes completed truth, FR directly carries implementation PRs, or PR body/auto-close semantics replace Work Item closeout.
- Operational boundaries: no GitHub mutating automation, task carrier contract, skills routing, gate-chain, or CLI implementation is introduced by this Work Item.
- Rollback or fallback expectations: revert this PR if the mapping weakens Work Item authority or makes GitHub Project/PR state authoritative over Loom closeout evidence.

## Acceptance Criteria

- [x] Phase, FR, Work Item, Project item, and PR mappings define authority boundary, locator/provenance, and forbidden use.
- [x] Project is defined as a view/organization carrier, not Loom truth.
- [x] Project `Status` values `Todo`, `In Progress`, and `Done` have explicit semantics.
- [x] `Done` is not treated as completed truth without closeout evidence.
- [x] FR does not directly carry implementation PRs.
- [x] Work Item remains the unique/default execution entry.
- [x] Native parent/sub-issue and `blocked-by/blocks` synchronization rules are explicit.
- [x] GitHub mapping can be consumed by later task carrier profile work.
