# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/check_cli_contract.py | .loom/specs/WI-1149/spec.md S1-S2 / A1 | WI-1149 / CLI contract negative fixtures | present | fixture evidence only | Re-run python3 tools/check_cli_contract.py after fixture changes. |
| EV-002 | behavior_evidence | skills/shared/scripts/loom_check.py | .loom/specs/WI-1149/spec.md S1-S2 / A2 | WI-1149 / source and installed loom_check negative fixtures | present | source/installed regression evidence only | Re-run source-self fixture checks after runtime changes. |
| EV-003 | test_evidence | src/skills/shared/scripts/loom_check.py | .loom/specs/WI-1149/spec.md A3-A4 | WI-1149 / source-generated parity | present | generated/source parity evidence only | Re-run skills surface and runtime parity checks after sync changes. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1149.md | EV-001 EV-002 EV-003 | WI-1149 / latest validation summary | present | PR handoff evidence | Refresh progress summary after final validation. |
