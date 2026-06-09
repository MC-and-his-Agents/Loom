# Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1283 | Issue open / branch active / PR pending / work item in progress | in_progress | primary | .loom/progress/WI-1283.md | .loom/specs/WI-1283/spec.md#wi-1283-suite-path-decision | none | .loom/progress/WI-1283.md#execution-ledger | .loom/specs/WI-1283/evidence-map.md | branch work/1283-repo-local-cli-local-validation; workspace_entry `.`; scheduler thread 019eabaf-92dc-7a52-a238-838f4c0bf4ac; worker T2 | Recheck issue, branch, head SHA, local alias map, PR metadata, hosted checks, and scheduler-owned gate before terminalizing; carrier state is tracking-only and does not close #1283 or #1259. |
