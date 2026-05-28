# WI-1138 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1138 is a narrow verify integration slice that consumes existing suite validate output only when an explicit profile or Work Item gate requires it; consumer boundary: scenario skill consumption, review locator expansion, closeout validation, reconciliation taxonomy, and E2E governance fixtures remain later Work Items under #1136/#1145; recheck condition: this change starts requiring suite validation for every target, runs evidence/carrier/consistency validators from verify, or changes frozen #1014-#1020 contracts.

## Goal

`loom verify` runs suite validation only when the current invocation, profile, or installed-state gate explicitly requires it.

## Scope

- In scope: `loom verify --item`, installed-state/profile `suite_validation` requirement parsing, read-only `suite validate` consumption, CLI contract fixtures, docs, and stale #1137 carrier terminalization.
- Out of scope: universal suite enforcement, `suite evidence validate`, `suite carrier validate`, consistency analysis, host writes, scenario skill changes, and closeout semantics.

## Key Scenarios

### Scenario S1

Given a valid installed-state with no suite validation requirement
When `loom verify --json` runs
Then verify passes without running suite validation.

### Scenario S2

Given declared suite command support but no profile or Work Item gate requirement
When `loom verify --json` runs
Then verify still passes without turning declared support into universal blocking validation.

### Scenario S3

Given installed-state profile requirements that mark suite validation required and name a suite item
When `loom verify --json` runs
Then verify runs `suite validate` for that item and passes when the suite is valid.

### Scenario S4

Given `loom verify --item WI-missing`
When the target lacks a valid suite path decision for that item
Then verify fails closed with the `suite validate` failure layer and payload.

## Acceptance Criteria

- A1: Verify output includes `suite_validation_requirement`.
- A2: Verify does not run suite validation when no profile or Work Item gate requires it.
- A3: Declared suite command support alone does not require suite validation.
- A4: Profile-required suite validation runs `suite validate` and passes with valid minimal suite artifacts.
- A5: Work Item gate-required suite validation blocks when `suite validate` blocks.
- A6: Verify remains read-only and does not run evidence/carrier/consistency validators.
- A7: CLI output remains gate evidence and does not replace Work Item, review, merge-ready, closeout, docs, or source truth.
- A8: The implementation does not introduce `/speckit.*` or `.specify/` surfaces.
