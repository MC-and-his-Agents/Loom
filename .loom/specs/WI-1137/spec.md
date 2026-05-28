# WI-1137 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1137 is a narrow doctor integration slice that checks installed-state declared suite command support against the CLI help command matrix; consumer boundary: verify profile enforcement, scenario skill consumption, review/closeout locator consumption, reconciliation taxonomy, and E2E governance fixtures remain later Work Items under #1136/#1145; recheck condition: this change starts running full suite validators from doctor, adds host writes, or changes frozen #1014-#1020 contracts.

## Goal

`loom doctor` reports whether a target that declares suite command support actually exposes the suite command surface in `loom help --json`, while still passing targets that do not declare suite support.

## Scope

- In scope: installed-state declared support parsing, suite command matrix drift detection, doctor payload check output, CLI contract fixtures, and docs for the declared support boundary.
- Out of scope: running `suite validate`, `suite evidence validate`, `suite carrier validate`, verify profile enforcement, closeout semantics, host writes, or scenario skill changes.

## Key Scenarios

### Scenario S1

Given a valid installed-state that does not declare suite command support
When `loom doctor --json` runs
Then doctor passes and reports `suite-command-surface` as not required.

### Scenario S2

Given a valid installed-state declaring existing suite commands
When `loom doctor --json` runs
Then doctor compares the declared commands with `loom help --json` and passes without running full suite validation.

### Scenario S3

Given a valid installed-state declaring a missing suite command
When `loom doctor --json` runs
Then doctor fails closed with a `suite-command-surface` finding and repair/help fallback.

## Acceptance Criteria

- A1: Doctor output includes a `suite-command-surface` check.
- A2: Undeclared suite command support passes and does not require suite command execution.
- A3: Declared suite command support passes only when the help matrix exposes the declared commands as `domain: suite`, `status: implemented`, and `json: true`.
- A4: Declared command drift fails closed with structured schema errors.
- A5: The implementation does not run full suite validators from doctor.
- A6: CLI output does not replace Work Item, review, merge-ready, closeout, or docs/source truth.
- A7: The implementation does not introduce `/speckit.*` or `.specify/` surfaces.
