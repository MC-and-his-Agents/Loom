# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/check_cli_contract.py | .loom/specs/WI-1153/spec.md S1-S2 / A1 | WI-1153 / governance chain fixture | present | fixture evidence only | Re-run python3 tools/check_cli_contract.py after closeout or reconciliation changes. |
| EV-002 | behavior_evidence | skills/shared/scripts/loom_flow.py | .loom/specs/WI-1153/spec.md A2 | WI-1153 / non-mutating host fixture inputs | present | closeout/reconciliation fixture inputs only | Re-run focused closeout/reconciliation fixture checks after CLI surface changes. |
| EV-003 | test_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-1153/spec.md A3 | WI-1153 / source-generated parity | present | generated/source parity evidence only | Re-run skills surface and runtime parity checks after sync changes. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1153.md | EV-001 EV-002 EV-003 | WI-1153 / latest validation summary | present | PR handoff evidence | Refresh progress summary after final validation. |
