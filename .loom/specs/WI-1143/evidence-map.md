# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-1143/spec.md S1-S4 | WI-1143 / reconciliation suite taxonomy / current branch | present | reconciliation audit evidence only | Re-run reconciliation and contract checks after runtime changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1143/plan.md validation commands | WI-1143 / CLI contract fixtures | present | CLI contract evidence only | Re-run python3 tools/check_cli_contract.py. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1143.md | EV-001 EV-002 | WI-1143 / latest validation summary | present | review / merge-ready / closeout evidence | Refresh progress summary after final validation. |
