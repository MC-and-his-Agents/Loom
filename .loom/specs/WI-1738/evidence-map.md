# Evidence Map

- Suite path: minimal.

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/loom.py | .loom/specs/WI-1738/spec.md S1 S2 S3 | WI-1738 / ship binding inference / branch work/1738-ship-inference | present | review / merge-ready / PR gate | Re-run after ship wrapper, host binding, metadata repair, merge, or closeout branch logic changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1738/spec.md S1 S2 S3 | WI-1738 / ship wrapper CLI contract / branch work/1738-ship-inference | present | review / merge-ready / PR gate | Re-run `tools/check_cli_contract.py --surface ship-wrapper` after ship CLI contract or fixture changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1738.md | EV-001 EV-002 | WI-1738 / latest validation summary / branch work/1738-ship-inference | present | merge-ready / PR gate / closeout / status | Refresh latest validation summary, PR body machine carrier, and review record after every non-carrier PR head change. |
