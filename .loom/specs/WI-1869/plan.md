# WI-1869 Plan

## Implementation Goal

Implement the smallest recovery polish needed for #1870-#1873 and leave v0.26.1 release work to #1874.

## Phases

### Phase 1

- Objective: implement core fixes.
- Deliverable: reconciliation native dependency mutation executor, release readback closeout-head guidance, terminal closeout review record path.
- Exit condition: targeted contract tests pass.

### Phase 2

- Objective: align consumers and UX.
- Deliverable: hosted closeout admission consumes carrier-only review; help and bilingual docs show closeout common path.
- Exit condition: governance-closeout and release-readback contracts pass.

### Phase 3

- Objective: prepare implementation PR.
- Deliverable: PR metadata, review record, local PR gate, hosted checks, merge.
- Exit condition: #1870-#1873 can close and #1874 can start release.

## Constraints

- Do not introduce a new gate scheduler.
- Do not broaden closeout command semantics beyond existing composed commands.
- Do not represent carrier-only closeout review as product implementation approval.
- Do not bump version or publish packages in this Work Item.

## Validation

- `python3 tools/check_cli_contract.py --surface release-readback`
- `python3 tools/check_cli_contract.py --surface governance-closeout`
- `python3 tools/check_cli_contract.py --surface closeout-wrapper`
- `python3 tools/check_cli_contract.py --surface pr-metadata`
- `python3 tools/check_cli_contract.py --surface runtime-upgrade`
- `python3 tools/loom.py skills release-check --json`
- `python3 tools/check_cli_contract.py --surface aggregate`

## Scenario Validation Mapping

- S1 -> automated validation strategy: `python3 tools/check_cli_contract.py --surface governance-closeout`.
- S2 -> automated validation strategy: `python3 tools/check_cli_contract.py --surface release-readback`.
- S3 -> automated validation strategy: `python3 tools/check_cli_contract.py --surface governance-closeout`.
- S4 -> structural validation strategy: README, README.zh-CN, CLI matrix, and `loom help --json` route readback.

## Test Strategy

- A1 -> test evidence: governance-closeout contract covers native dependency removal apply.
- A2 -> test evidence: release-readback contract covers closeout-head release commit guidance.
- A3 -> test evidence: governance-closeout contract covers terminal closeout review record output.
- A4 -> test evidence: governance-closeout contract covers hosted closeout admission consumption.
- A5 -> test evidence: help/readme docs plus aggregate CLI contract cover common path guidance.
- A6 -> test evidence: aggregate CLI contract and skills release-check cover full local validation.

## Dependencies

- Blocking inputs: none.
- Required coordination: #1874 release waits until this implementation PR is merged.
- Rollback boundary: revert this branch before release; after release, use patch release repair/readback path.

## Ready For Implementation

- [x] Scope and non-goals are clear.
- [x] Validation path is defined.
- [x] Review and gate boundaries remain explicit.
- [x] Release follow-up is separated into #1874.
