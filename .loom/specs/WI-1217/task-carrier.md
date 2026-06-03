# Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1217 | Issue open / branch active / PR #1227 open | in_progress | primary | .loom/work-items/WI-1217.md | #1218-#1226 child issue tree | .loom/specs/WI-1217/spec.md#scenarios | .loom/specs/WI-1217/plan.md#steps | .loom/specs/WI-1217/plan.md#acceptance-mapping | branch work/1217-metadata-only-adoption; target-local workspace `.`; carrier is tracking-only and does not replace Work Item or recovery truth | Recheck issue tree, PR, checks, merge commit, target branch, release/no-release decision, and closeout evidence before final closeout. |
