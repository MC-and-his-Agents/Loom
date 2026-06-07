# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/check_cli_contract.py | .loom/specs/WI-1323/spec.md S1 S2 S3 / AC-1 AC-2 AC-4 | WI-1323 / governance intensity escalation and abuse fixture behavior | present | review / merge-ready / PR gate / closeout / status | Re-run targeted CLI contract checks after fixture or gate behavior changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1323/plan.md validation mapping | WI-1323 / targeted fixture matrix / final pre-review local run completed in 193.56s | present | review / merge-ready / PR gate / closeout / status | Re-run after any fixture, carrier, or gate input changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1323.md | EV-001 EV-002 plus suite validate, pr-gate dry check, git diff, no-release, review, hosted checks, controlled merge, and closeout evidence | WI-1323 / latest validation summary / PR pending | present | merge-ready / closeout / status | Refresh progress summary after validation, PR creation, head changes, hosted checks, merge, or closeout. |
