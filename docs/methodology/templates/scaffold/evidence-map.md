# Evidence Map

## Context

- Work Item locator:
- FR / parent locator:
- Scope:
- Suite path:
- Current `HEAD`:
- PR locator, or `not_applicable` rationale:
- Host state locator, or `not_applicable` rationale:

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` |  | required |  |  |
| `plan.md` |  | required |  |  |
| suite path decision |  | candidate / optional / not_applicable |  |  |
| execution breakdown / task carrier |  | candidate / optional / deferred / not_applicable |  |  |
| review record |  | optional / required / not_applicable |  |  |
| merge-ready basis |  | optional / required / not_applicable |  |  |
| host state |  | required / not_applicable |  |  |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence |  | spec scenario / acceptance locator | Work Item / scope / head / PR | present / stale / missing / conflict / not_applicable | review / merge-ready / closeout / status |  |
| EV-002 | test_evidence |  | plan validation / test strategy locator | Work Item / scope / head / PR | present / stale / missing / conflict / not_applicable | review / merge-ready / closeout / status |  |
| EV-003 | fresh_verification_input |  | evidence row ids | head / reviewed head / PR head / validation summary | present / stale / missing / conflict / not_applicable | merge-ready / closeout / status |  |

## Not Applicable / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
|  | not_applicable / deferred |  |  |  |  |

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption:
- Generated surface sync:
- Drift check requirement:

