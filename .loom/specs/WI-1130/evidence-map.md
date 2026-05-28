# WI-1130 Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/loom.py | `.loom/specs/WI-1130/spec.md` S1-S3 | WI-1130 / scope / current branch | present | review / merge-ready evidence only | Re-run CLI contract fixtures after changing validation logic. |
| EV-002 | test_evidence | tools/check_cli_contract.py | `.loom/specs/WI-1130/plan.md` validation commands | WI-1130 / CLI contract fixtures | present | review / merge-ready evidence only | Re-run `python3 tools/check_cli_contract.py`. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1130.md | EV-001 EV-002 | WI-1130 / latest validation summary | present | review / merge-ready evidence only | Refresh progress summary after final validation. |
