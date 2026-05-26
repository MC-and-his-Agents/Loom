# PR Slicing

- Schema marker: loom-pr-slicing/v1

## Slicing Goal

- Goal:
- Delivery planning locator:
- Issue-tree plan locator:
- Slicing owner:
- Freshness status: current | stale | superseded

## Input Locators

- Phase locator:
- FR locator:
- Candidate Work Item locators:
- Dependency / blocked-by locator:
- Existing PR locator or `not_applicable` rationale:
- Conversation locator or `not_applicable` rationale:

## Candidate Work Items

### Work Item 1

- Locator:
- Parent FR:
- Scope:
- Non-goals:
- Validation entry:
- Closeout condition:
- Project Status:

## Dependency Read

- Blocking dependencies:
- Sequencing only:
- Independent candidates:
- Dependency risks:

## Same PR Decision

- Decision: single_pr | split_pr | defer_decision | not_applicable
- Rationale:
- Primary Work Item:
- Additional Work Item links:
- Required PR count:

## Same PR Conditions

- Shared parent FR or cross-FR rationale:
- Scope purity statement:
- Review risk statement:
- Validation coverage statement:
- PR body requirements:
- Closeout requirements:

## Split PR Conditions

- Required split triggers:
- Risk domains that require separate PRs:
- Independent review requirements:
- Independent merge / closeout requirements:
- Deferred or unstable scope:

## PR Body Contract

- Primary `Loom Work Item`:
- Related Phase / FR:
- Spec / plan locator:
- Validation summary:
- Additional Work Item links:
- Risks and follow-ups:
- Machine carrier locator or `not_applicable` rationale:

## Review Risk

- Required reviewer perspectives:
- Scope risks:
- Validation risks:
- Host / Project status risks:
- Risk reduction action:

## Validation Matrix

| Work Item | Evidence Required | Command / Locator | Status |
|---|---|---|---|
|  |  |  | pending |

## Merge-ready Consumption

- PR head SHA requirement:
- Review record requirement:
- Validation summary requirement:
- PR body linkage requirement:
- Required checks:
- Project Status consistency:

## Closeout Consumption

| Work Item | PR | Head SHA | Merge Commit | Project Status | Closeout Comment |
|---|---|---|---|---|---|
|  |  |  |  | pending | pending |

## Freshness Rule

- Stale when:
- Superseded by:
- Revalidation entry:
