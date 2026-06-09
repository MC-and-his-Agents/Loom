# Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1282 | Issue open / branch active / PR pending / work item in progress | in_progress | primary | .loom/progress/WI-1282.md | .loom/specs/WI-1282/spec.md#suite-path-decision | none | .loom/progress/WI-1282.md#command-group-contract | .loom/specs/WI-1282/evidence-map.md | branch work/1282-repo-local-cli-workflow-steps; workspace_entry `.`; scheduler thread 019eabaf-92dc-7a52-a238-838f4c0bf4ac; worker T1 | Recheck issue, branch, head SHA, command group contract, PR metadata, hosted checks, and scheduler-owned gate before terminalizing; carrier state is tracking-only and does not close #1282 or #1259. |
