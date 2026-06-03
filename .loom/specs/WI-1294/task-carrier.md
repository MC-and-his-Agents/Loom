# Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1294 | Issue open / branch active / PR pending | in_progress | primary | .loom/work-items/WI-1294.md | v0.13.10 release follow-up | .loom/specs/WI-1294/spec.md#scenario-s1 | .loom/specs/WI-1294/plan.md#phase-1 | .loom/specs/WI-1294/plan.md#validation | issue #1294; branch work/1294-release-followup; target-local workspace `.` | Recheck issue, PR, CI, merge commit, tag, GitHub Release, npm package, and #1217 closeout evidence before final closeout. |
