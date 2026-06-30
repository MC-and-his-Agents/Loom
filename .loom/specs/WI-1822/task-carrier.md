# Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1822 | Issue open / branch active / PR pending | in_progress | primary | .loom/work-items/WI-1822.md | .loom/specs/WI-1822/task-carrier.md#fix-scope | .loom/specs/WI-1822/evidence-map.md#evidence-rows | .loom/progress/WI-1822.md | .loom/specs/WI-1822/evidence-map.md | workspace_entry `.`; branch `work/1822-normalize-closeout-checkpoint`; implementation head `37c6acb11c212afb25ac669243662460c36bbc0d`; issue #1822 | Recheck issue / PR / branch / head binding before review, merge, release, and closeout. |

## Fix Scope

- Normalize `closeout` checkpoint input to `closed_out` in the shared Loom flow runtime copies.
- Add a focused CLI contract check so future resume/state-check consumption keeps accepting real terminal carrier wording.
