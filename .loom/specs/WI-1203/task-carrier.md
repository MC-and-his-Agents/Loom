# Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1203 | Issue open / branch active / PR pending | in_progress | primary | .loom/work-items/WI-1203.md | not required for this release closeout | .loom/specs/WI-1203/spec.md#scenarios | .loom/specs/WI-1203/plan.md#steps | .loom/specs/WI-1203/plan.md#acceptance-mapping | branch work/1203-release-version-bump; target-local workspace `.`; carrier is tracking-only and does not replace Work Item or recovery truth | Recheck issue, PR, checks, and main release workflow before merge-ready and closeout. |
