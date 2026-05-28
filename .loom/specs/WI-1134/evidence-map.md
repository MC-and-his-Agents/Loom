# WI-1134 Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | skills/shared/scripts/loom_flow.py | `.loom/specs/WI-1134/spec.md` S1-S3 | WI-1134 / gate integration / current branch | present | review / merge-ready evidence only | Re-run flow and review record checks after changing suite gate validation behavior. |
| EV-002 | test_evidence | tools/check_cli_contract.py | `.loom/specs/WI-1134/plan.md` validation commands | WI-1134 / CLI contract fixtures | present | review / merge-ready evidence only | Re-run `python3 tools/check_cli_contract.py`. |
| EV-003 | behavior_evidence | tools/loom.py | `.loom/specs/WI-1134/spec.md` A5 | WI-1134 / top-level merge-ready wrapper | present | merge-ready evidence only | Re-run top-level `loom merge-ready --json` after changing delegated wrappers. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1134.md | EV-001 EV-002 EV-003 | WI-1134 / latest validation summary | present | review / merge-ready evidence only | Refresh progress summary after final validation. |
