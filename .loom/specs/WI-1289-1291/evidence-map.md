# WI-1289-1291 Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | skills/shared/scripts/loom_flow.py | .loom/specs/WI-1289-1291/spec.md S1 S2 S3 / A1 A2 A3 A4 A5 | WI-1289-1291 / merge check-run PR gate consumption and post-merge review bypass diagnostics | present | build / review / merge-ready / closeout | Re-run PR gate, controlled merge check, runtime parity, and closeout diagnostics after runtime or carrier changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1289-1291/plan.md#validation / A1 A2 A4 A5 | WI-1289-1291 / CLI fixtures, demo bootstrap fixture, and hosted gate surfaces | present | review / merge-ready / hosted checks | Re-run CLI contract, demo bootstrap, skills/release/package checks, PR gate, and hosted checks after repair commits. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1289-1291.md | EV-001 EV-002 | WI-1289-1291 / current validation summary and review evidence | present | review / merge-ready / closeout evidence | Refresh progress and review evidence after final local validation, PR body readback, hosted checks, controlled merge, and post-merge closeout. |
