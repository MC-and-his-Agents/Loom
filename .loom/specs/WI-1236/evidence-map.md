# WI-1236 Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/check_cli_contract.py | .loom/specs/WI-1236/spec.md S1 S2 S3 S4 | WI-1236 / branch work/1236-hotcp-regression-fixtures / HotCP stale active closeout fixture | present | build / review / merge-ready / PR gate | Re-run governance-closeout after changing repair, workspace retire, idle fact-chain, or fixture behavior. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1236/plan.md validation | WI-1236 / local py_compile and governance-closeout validation | present | build / review / merge-ready / PR gate | Re-run focused validation after Python or fixture changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1236.md | EV-001 EV-002 | WI-1236 / latest local validation summary / branch work/1236-hotcp-regression-fixtures | present | review / merge-ready / closeout | Refresh after validation, PR creation/update, hosted checks readback, merge, or closeout. |
| EV-004 | structural_evidence | .loom/status/current.md | WI-1236 active fact-chain/status carrier | WI-1236 / current branch | present | build / review / merge-ready / closeout | Refresh carrier/shadow after status or init-result changes. |
