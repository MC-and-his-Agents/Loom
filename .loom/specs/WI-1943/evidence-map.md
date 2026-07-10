# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1943.md
- FR / parent locator: #1888
- Scope: terminal closeout carrier PR gate consumption.
- Suite path: minimal
- Current `HEAD`: e9ddc9090a28954610e7bd99b586943a7470d517 implementation baseline before review carrier.
- PR locator: #1944
- Host state locator: issue #1943.

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | S1 S2 / A1 A2 | WI-1943 / terminal closeout gate consumption | present | review / merge-ready / closeout / status | Recheck after retained PR gate or closeout backlink semantics change. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py --surface controlled-merge --surface governance-closeout` | S1 S2 / A1 A2 | WI-1943 / focused CLI fixtures | present | review / merge-ready / closeout / status | Rerun after `loom_flow.py` or CLI contract fixtures change. |
| EV-003 | test_evidence | `python3 tools/check_npm_package.py --surface aggregate` | runtime copy/hash sync | plugin/runtime payload | present | review / release-check / PR gate | Rerun after plugin payload or runtime copies change. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1943.md | EV-001 EV-002 EV-003 | WI-1943 / validation summary | present | merge-ready / closeout / status | Refresh after PR metadata, hosted checks, merge, or closeout evidence changes. |

## Deferred / Out Of Scope

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| demo consumer profile failure | deferred | Existing `loom_check contract-only` consumer profile failure is outside WI-1943. | WI-1943 review / PR gate | Activate when fixing demo consumer profile surface. | follow-up issue |
