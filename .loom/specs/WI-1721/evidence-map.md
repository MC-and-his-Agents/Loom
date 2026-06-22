# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1721.md`
- FR / parent locator: GitHub issue #1721
- Scope: Codex plugin source, marketplace source, and runtime cache readback.
- Suite path: minimal

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1 S2 S3 | WI-1721 / plugin_payload_readback | present | build / review / merge-ready / closeout | Re-run host doctor and targeted contract check after host readback code changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | A1 A2 A3 A4 | WI-1721 / adoption-host-metadata surface | present | build / review / merge-ready | Re-run `python3 tools/check_cli_contract.py --surface adoption-host-metadata`. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1721.md` | EV-001 EV-002 | WI-1721 / latest validation summary | present | merge-ready / closeout / status | Refresh after final validation or head changes. |
