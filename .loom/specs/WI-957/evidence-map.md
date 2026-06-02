# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-957/spec.md S1 S2 S3 S4 / A1 A2 A3 A4 A5 | WI-957 / pre-review readiness-cost guard | present | pre-review / review / merge-ready / closeout / status | Re-run focused pre-review guard smoke after guard changes. |
| EV-002 | test_evidence | src/skills/shared/scripts/loom_check.py | .loom/specs/WI-957/spec.md A1 A2 A4 | WI-957 / source loom_check fixture | present | review / merge-ready / closeout / status | Re-run `python3 tools/loom_check.py --profile source --source-surface contract-only .` after fixture changes. |
| EV-003 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-957/spec.md A2 A4 | WI-957 / CLI wrapper contract | present | review / merge-ready / closeout / status | Re-run `python3 tools/check_cli_contract.py` after CLI wrapper or flow output changes. |
| EV-004 | fresh_verification_input | .loom/progress/WI-957.md | EV-001 EV-002 EV-003 plus git diff, focused rg, skills surface, loom_check, CLI contract, suite, PR gate, and closeout checks | WI-957 / latest validation summary / PR pending | present | merge-ready / closeout / status | Refresh progress summary after validation, PR creation, head changes, or additional checks. |
