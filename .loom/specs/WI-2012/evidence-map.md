# WI-2012 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | VERSION | S1 / A1 candidate version behavior | work_item=WI-2012; candidate=v0.28.1 | present | review / package validation / release workflow | Re-run version surface validation after any release metadata or payload change. |
| EV-002 | test_evidence | .loom/progress/WI-2012.md | S1 / A1 / A2 package validation | work_item=WI-2012; branch=work/2012-cli-release-0.28.1 | present | review / PR gate / release workflow | Refresh the recorded command summary after package, release-surface, or carrier changes. |
| EV-003 | fresh_verification_input | .loom/status/current.md | EV-001 EV-002 / review readiness | work_item=WI-2012; candidate branch | present | merge-ready / PR gate | Refresh after validation and again after review/head changes. |
