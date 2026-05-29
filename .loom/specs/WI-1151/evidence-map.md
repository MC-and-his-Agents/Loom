# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_check.py | .loom/specs/WI-1151/spec.md S1-S3 / A2-A3 | WI-1151 / source and installed scaffold mutation boundary | present | fixture evidence only | Re-run source-self fixture after helper changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1151/spec.md A1 | WI-1151 / scaffold CLI contract fixtures | present | contract regression evidence only | Re-run focused CLI contract checks after scaffold changes. |
| EV-003 | parity_evidence | skills/shared/scripts/loom_check.py; .loom/bin/loom_check.py; examples/new-project/.loom/bin/loom_check.py | .loom/specs/WI-1151/spec.md A4 | WI-1151 / runtime copy parity | present | generated/source parity evidence only | Re-run skills surface and contract-only checks after sync changes. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1151.md | EV-001 EV-002 EV-003 | WI-1151 / latest validation summary | present | review / merge-ready evidence | Refresh after final local validation. |
