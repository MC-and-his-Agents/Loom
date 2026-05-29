# Spec

## Suite Contract

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: #1142 is a narrow closeout consumer Work Item that validates existing suite evidence/carrier locator consumption instead of requiring full path artifacts; consumer boundary: closeout, review, and merge-ready may consume the minimal suite evidence without treating skipped full path artifacts as completed; recheck condition: #1142 starts defining new CLI product scope, domain contracts, readiness checks, or consistency analyze output.
- Consumes:
  - Work Item / FR locator: #1142 / #1136
  - Story Readiness source: GitHub Work Item body is the scoped carrier.
  - Story scenario source: scenarios are authored below.
  - Story Business Confirmation source: governance behavior only, with no business-semantics carrier.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: closeout consumes suite gate validation and blocks missing/stale suite evidence.
- Locator:
  - Spec locator: .loom/specs/WI-1142/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: #1142, #1136, docs/methodology/harness/full-spec-suite-cli-surface.md, docs/methodology/templates/evidence-map.md, docs/methodology/templates/consistency-analysis.md
  - Freshness rule: re-run closeout and CLI contract checks after changing closeout gate consumption.

## Goal

- Prevent `loom closeout` from passing only because a PR is merged when suite evidence is missing or stale.
- Make closeout consume suite evidence, carrier, and consistency-analysis locators as evidence inputs while preserving closeout and host state as separate truth.

## Scope

- In scope: closeout gate payload, required closeout subchecks for suite evidence/carrier validation, closeout consumed locator output, CLI contract coverage, generated runtime copies, and #1142 suite carriers.
- Out of scope: automatic issue close without closeout evidence, new consistency analyze implementation, parallel closeout truth, `/speckit.*` commands, and `.specify/` layout.

## Key Scenarios

### Scenario S1

Given
- a Work Item has a formal suite and a merged PR closeout context

When
- `loom closeout` evaluates closeout readiness

Then
- closeout consumes suite evidence and carrier validation results before it can pass.

### Scenario S2

Given
- a Work Item has PR merge evidence but its suite evidence map is missing or stale

When
- `loom closeout` runs

Then
- closeout fails closed and reports suite evidence validation as the blocking input.

### Scenario S3

Given
- suite evidence, task carrier, PR head, merge commit, target branch, issue, Project, and reconciliation readbacks are all present

When
- `loom closeout` returns its payload

Then
- suite/evidence/consistency locators appear as consumed evidence and do not replace Work Item, merge-ready, closeout, Project, or docs/source truth.

## Behavior Evidence

- Story scenario mapping: S1-S3 are issue-scoped and authored in this file.
- Story readiness locator: #1142 body is the readiness source.
- Story business confirmation locator: none required for this governance-only behavior.
- Scenario coverage:
  - S1 -> expected behavior evidence locator: src/skills/shared/scripts/loom_flow.py closeout suite subchecks.
  - S2 -> expected behavior evidence locator: tools/check_cli_contract.py missing evidence negative fixture.
  - S3 -> expected behavior evidence locator: closeout payload `suite_gate_validation.consumed_locators`.
- Expected evidence locator: .loom/specs/WI-1142/evidence-map.md
- Freshness rule: evidence is fresh only after local closeout and contract checks pass on the current head.
- Execution ledger acceptance locator: .loom/progress/WI-1142.md
- Behavior-bearing change rationale: closeout gate behavior changes and is covered by S1-S3.

## Exceptions And Boundaries

- Failure modes: missing evidence-map, stale evidence, missing task carrier, stale review/merge-ready/PR evidence, unreadable Project, and reconciliation drift fail closed.
- Operational boundaries: host PR merge state is evidence only; closeout pass requires Loom evidence and host readback.
- Rollback or fallback expectations: revert closeout suite subcheck wiring and rerun contract checks if closeout blocks valid completed Work Items.

## Acceptance Criteria

- [ ] A1: Closeout payload exposes `suite_gate_validation` with surface `closeout`.
- [ ] A2: Closeout blocks when suite evidence validation blocks, even if PR merge evidence exists.
- [ ] A3: Closeout consumed locators include evidence-map, consistency-analysis key, and task-carrier locators.
- [ ] A4: CLI contract tests cover closeout suite consumption and missing evidence fail-closed behavior.
- [ ] A5: Generated runtime surfaces stay synchronized and no CLI output becomes closeout truth.
