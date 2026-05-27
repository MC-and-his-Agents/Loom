# WI-1051 Spec

## Goal

Synchronize source skills and generated skills surface so installed Loom skills can read the full suite, execution breakdown, task carrier, evidence-map, and consistency-analysis contracts while drift checks fail closed when docs, source references, or generated skills diverge.

## Scope

- In scope:
  - Source shared references copied from docs authority for `spec-suite`, its linked scaffold templates, `execution-breakdown`, `task-carrier-contract`, `evidence-map`, and `consistency-analysis`.
  - Generated `skills/` surface refreshed from `src/skills`.
  - `skills_surface.py check` detects docs -> source reference drift and source -> generated skills drift.
  - Scenario skill text and route matrix expose installed-state locators for the synchronized references.
  - #1036 deferred source/generated sync need is consumed by #1051 evidence.
- Out of scope:
  - Redefining #1014-#1019 core contracts.
  - Reworking #1049 GitHub task carrier profile mapping or #1050 scenario routing semantics.
  - Implementing or planning #1052 CLI command surface.
  - Creating new source of truth in generated skills.

## Key Scenarios

### Scenario 1

Given
- docs authority files define full suite, execution breakdown, task carrier, evidence-map, and consistency-analysis contracts

When
- `python3 tools/skills_surface.py check` runs

Then
- it fails closed if the source shared reference copies drift from those docs files, and it still fails closed if generated `skills/` drifts from `src/skills`.

### Scenario 2

Given
- an installed skill needs to consume full path readiness, task carrier locators, evidence-map rows, or consistency-analysis classifications

When
- it reads the installed skills runtime surface

Then
- the same shared references are available under `skills/shared/references/...` and linked from the scenario skills without making generated skills the authority.

### Scenario 3

Given
- #1036 was closed as deferred source/generated sync work

When
- #1051 closes

Then
- the closeout evidence states how #1036 was consumed or superseded, and no standalone #1036 reopen is required.

## Behavior Evidence

- Story scenario mapping: not_applicable; this Work Item changes skill/install surface references, not product story semantics.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; pure governance skill-surface synchronization.
- Scenario coverage: focused `rg` checks and `skills_surface.py check` show full suite, task carrier, evidence-map, consistency-analysis, source/generated, generated skills, and drift boundaries in source and generated surfaces.
- Expected evidence locator: PR for #1051 and #1051 completion comment consuming #1036.
- Freshness rule: stale if docs authority, source shared references, generated skills, validation evidence, PR head, or merge commit no longer match.
- Execution ledger acceptance locator: `.loom/specs/WI-1051/spec.md`.

## Exceptions And Boundaries

- Failure modes: source reference copy drifts from docs authority, generated skills drift from source, installed skill links cannot read required shared references, or #1036 is treated as completed without #1051 evidence.
- Operational boundaries: generated `skills/` is install surface only; docs and source shared references remain the authority chain.
- Rollback or fallback expectations: revert this PR if it makes generated skills authoritative, changes #1014-#1019 contract semantics, or introduces #1052 CLI scope.

## Acceptance Criteria

- [x] Source shared references include docs-synced full suite, linked scaffold templates, execution breakdown, task carrier, evidence-map, and consistency-analysis contracts.
- [x] Scenario skills and route matrix expose installed-state locators for these references.
- [x] `skills_surface.py check` detects docs -> source reference drift and source -> generated skills drift.
- [x] Checked-in generated `skills/` matches `src/skills`.
- [x] #1036 deferred source/generated sync need is explicitly consumed by #1051 closeout evidence.
- [x] No #1052 CLI command surface or #1014-#1019 core contract redefinition is introduced.
