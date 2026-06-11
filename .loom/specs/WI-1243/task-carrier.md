# WI-1243 Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| repo_tasks_md | `.loom/work-items/WI-1243.md` | in progress | in_progress | primary | `.loom/work-items/WI-1243.md` | `.loom/specs/WI-1243/execution-breakdown.md#unit-runtime-carrier-plan` | `.loom/specs/WI-1243/spec.md#scenarios` | `.loom/specs/WI-1243/plan.md#steps` | `.loom/specs/WI-1243/evidence-map.md` | worker-scoped runtime-carrier migration plan | Refresh before scheduler gate and after PR metadata changes. |
