# WI-1717 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1717.md
- Parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1711
- Scope: minimal regression coverage for CLI/plugin freshness and payload hash stability.
- Suite path: minimal
- Current `HEAD`: refreshed before PR.
- Host state locator: https://github.com/MC-and-his-Agents/Loom/issues/1717

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/loom.py | S1 S2 S3 | WI-1717 / freshness output contract | present | review / merge-ready / closeout | Re-run adoption-host-metadata after freshness output changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | A1 A2 A3 A4 | WI-1717 / adoption-host-metadata surface | present | review / merge-ready | Re-run `python3 tools/check_cli_contract.py --surface adoption-host-metadata`. |
| EV-003 | test_evidence | test/plugin_payload_hash_test.py | A5 | WI-1717 / payload hash stability | present | review / merge-ready | Re-run `python3 test/plugin_payload_hash_test.py`. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1717.md | EV-001 EV-002 EV-003 | WI-1717 / current head validation summary | present | merge-ready / closeout / status | Refresh after PR head changes. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1717-build-evidence.json | EV-001 EV-002 EV-003 EV-004 | WI-1717 / integrated build evidence | present | build / review / merge-ready | Refresh after validation or ownership scope changes. |
| EV-006 | behavior_evidence | .loom/specs/WI-1717/implementation-contract.md | S1 S2 S3 A1 A2 A3 A4 A5 | WI-1717 / implementation boundary | present | review / merge-ready | Refresh if ownership, boundaries, or regression commitments change. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| v0.19.0 release readback | deferred | Release closeout is owned by #1718. | release / parent closeout | Recheck during release PR. | https://github.com/MC-and-his-Agents/Loom/issues/1718 |
