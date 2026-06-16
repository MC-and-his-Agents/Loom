# WI-1232 Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/check_cli_contract.py | .loom/specs/WI-1232/spec.md S1 S2 S3 S4 | WI-1232 / idle and active fail-closed read-surface behavior / branch work/1232-idle-read-surfaces | present | build / review / scheduler gate | Re-run `python3 tools/check_cli_contract.py --surface governance-closeout` after changing fact-chain/status/governance read surfaces. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1232/plan.md validation | WI-1232 / focused compile and governance-closeout fixture validation / branch work/1232-idle-read-surfaces | present | build / review / scheduler gate | Re-run compile and focused behavior checks after changing Python files or runtime copies. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1232.md | EV-001 EV-002 | WI-1232 / latest local validation summary / branch work/1232-idle-read-surfaces | present | scheduler gate handoff | Refresh progress summary after final validation, PR metadata readback, hosted checks, or head changes. |
