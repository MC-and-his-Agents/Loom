# Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/check_cli_contract.py | S1 / A1 | WI-1851 / current PR head | present | review / merge-ready / closeout | Rerun aggregate after PR intent changes. |
| EV-002 | behavior_evidence | tools/check_cli_contract.py | S2 / A2 | WI-1851 / current PR head | present | review / merge-ready / closeout | Rerun aggregate after metadata render/preflight changes. |
| EV-003 | behavior_evidence | tools/check_cli_contract.py | S3 / A3 | WI-1851 / current PR head | present | review / merge-ready / closeout | Rerun aggregate after readiness output changes. |
| EV-004 | behavior_evidence | README.md; README.zh-CN.md; docs/methodology/harness/cli-command-matrix.md; src/skills/route-matrix.md | S4 / A4 | WI-1851 / current PR head | present | review / merge-ready / closeout | Rerun skills generate/check after route text changes. |
| EV-005 | test_evidence | latest validation summary in .loom/progress/WI-1851.md | A5 | WI-1851 / current PR head | present | review / merge-ready / closeout | Refresh validation summary after final test run. |
| EV-006 | fresh_verification_input | .loom/progress/WI-1851.md | EV-001 EV-002 EV-003 EV-004 EV-005 | WI-1851 / current PR head | present | merge-ready / closeout | Rerun targeted checks after any source, docs, skills, or plugin metadata change. |
