# Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | S1 S2 S3 S4 S5 / AC-1 AC-2 AC-3 AC-4 AC-5 | WI-1230-1231 / current head | present | review / merge-ready / closeout | Re-run runtime parity and carrier closeout-sync smoke after changing shared runtime or CLI wrapper. |
| EV-002 | test_evidence | tools/check_cli_contract.py | AC-1 AC-2 AC-3 AC-4 AC-5 | WI-1230-1231 / CLI contract fixture | present | review / merge-ready / closeout | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py` after changing CLI contract behavior. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1230-1231.md | EV-001 EV-002 | WI-1230-1231 / latest validation summary | present | merge-ready / closeout | Refresh progress summary after PR checks, controlled merge, and post-merge closeout. |
