# WI-1150 Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_check.py | .loom/specs/WI-1150/spec.md S1-S2 / AC-1 AC-2 | WI-1150 / stale and host conflict fixture code | present | review / merge-ready / closeout fixture evidence | Re-run source-self fixture after changing fixture code. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1150/plan.md validation commands | WI-1150 / existing suite taxonomy fixtures | present | test evidence only | Re-run CLI contract checks after changing suite validation assumptions. |
| EV-003 | test_evidence | skills/shared/scripts/loom_check.py | generated surface sync | WI-1150 / source-generated parity | present | generated/runtime parity evidence | Re-run skills surface check after syncing generated files. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1150.md | EV-001 EV-002 EV-003 | WI-1150 / latest validation summary | present | PR evidence | Refresh progress summary after final validation. |
