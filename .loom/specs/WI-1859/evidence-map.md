# Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/check_cli_contract.py | S1 / A1 | WI-1859 / current PR head | present | review / merge-ready / closeout | Rerun runtime-upgrade surface after runtime-upgrade prepare/pr changes. |
| EV-002 | behavior_evidence | tools/check_cli_contract.py | S2 / A1 | WI-1859 / current PR head | present | review / merge-ready / closeout | Rerun runtime-upgrade surface after PR metadata orchestration changes. |
| EV-003 | behavior_evidence | tools/check_cli_contract.py | S3 / A2 A3 | WI-1859 / current PR head | present | review / merge-ready / closeout | Rerun runtime-upgrade surface after closeout host readback or carrier sync changes. |
| EV-004 | documentation_evidence | README.md; README.zh-CN.md; docs/methodology/harness/cli-command-matrix.md; src/skills/route-matrix.md; skills/route-matrix.md; plugins/loom/skills/route-matrix.md | S4 / A4 A5 | WI-1859 / current PR head | present | review / merge-ready / closeout | Rerun skills generate/check and aggregate after route text changes. |
| EV-005 | package_evidence | plugins/loom/.codex-plugin/plugin.json | A5 | WI-1859 / current PR head | present | release readiness / package checks | Rerun `tools/stamp_plugin_payload_metadata.py` and package checks after plugin payload changes. |
| EV-006 | fresh_verification_input | .loom/progress/WI-1859.md | EV-001 EV-002 EV-003 EV-004 EV-005 | WI-1859 / current PR head | present | merge-ready / closeout | Refresh validation summary after final test run. |
