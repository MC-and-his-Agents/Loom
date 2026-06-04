# Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | .loom/specs/WI-1302/spec.md | S1 S2 S3 / AC-1 AC-2 AC-3 AC-4 | WI-1302 / gate behavior | present | review / merge-ready / closeout evidence | Recheck spec after gate behavior changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | AC-1 AC-2 AC-3 AC-4 | WI-1302 / contract check | present | review / merge-ready / closeout evidence | Rerun `tools/check_cli_contract.py` after changing gate behavior. |
| EV-003 | behavior_evidence | .loom/specs/WI-1302/consistency-analysis.md | consistency analysis | WI-1302 / suite consistency | present | review / merge-ready / closeout evidence | Refresh consistency analysis after spec or plan changes. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1302.md | EV-001 EV-002 EV-003 | WI-1302 / latest validation summary | present | review / merge-ready / closeout evidence | Refresh progress summary after validation changes. |
