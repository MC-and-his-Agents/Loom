# Spec

## Suite Contract

- Suite path: minimal
- Work Item / FR locator: #1149 / #1145
- Story Readiness source: GitHub Work Item body is the scoped carrier.
- Story Business Confirmation source: governance regression only; business semantics are not required.
- Full suite artifacts not_applicable: rationale: #1149 is a narrow negative fixture Work Item; consumer boundary: suite validate, CLI contract checks, and source/installed loom_check fixtures do not require full-path planning artifacts for this Work Item carrier; recheck condition: broaden to full suite if #1149 starts owning cross-artifact integration, evidence freshness, host conflict, scaffold, PR gate, merge-ready, closeout, or parent reconciliation behavior.

## Goal

Add fail-closed regression coverage for:

- missing full required artifact validation;
- minimal path skip records missing rationale, consumer boundary, and recheck condition.

## Scope

In scope:

- `tools/loom.py` missing-input shape for invalid skip-rationale fields.
- `tools/check_cli_contract.py` negative fixture assertions.
- shared `loom_check` source/installed fixture consumption.
- generated/runtime/bin/example synchronization.

Out of scope:

- evidence freshness fixtures;
- stale host state or carrier conflict fixtures;
- scaffold dry-run/apply fixtures;
- generated-skill parity fixture as its own Work Item;
- PR gate, merge-ready, closeout, Project, #1145, or #1107 reconciliation.

## Scenarios

### Scenario S1

Given a full suite fixture declares `suite-index.md` but omits a required `plan.md`
When `loom suite validate --target <fixture> --item <item> --json` runs
Then the validator returns `result=block`, `fail_closed_reason=missing_required_artifact`, structured blocking gaps, remediation direction, failure taxonomy, and missing input for the absent artifact.

### Scenario S2

Given a minimal suite fixture records full artifact skips without rationale, consumer boundary, or recheck condition
When `loom suite validate --target <fixture> --item <item> --json` runs
Then the validator returns `result=block`, the invalid skip-rationale failure kind, structured blocking gaps, remediation direction, failure taxonomy, and missing-input evidence for the missing skip fields.

## Acceptance Criteria

- A1: `tools/check_cli_contract.py` asserts both negative fixtures block with expected taxonomy, blocking gaps, remediation, and missing-input shape.
- A2: `loom_check` source-self and installed pre-merge fixture paths consume the same negative fail-closed behavior.
- A3: source/generated/runtime/bin/example copies remain synchronized.
- A4: no `/speckit.*` command name or `.specify/` layout is introduced.
