# Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1257 | Issue open / branch active / PR pending | in_progress | primary | .loom/work-items/WI-1257.md | .loom/specs/WI-1257/spec.md#suite-path-decision | none | .loom/specs/WI-1257/spec.md#suite-path-decision | .loom/specs/WI-1257/evidence-map.md | branch `work/1257-check-cli-surfaces-closeout`; workspace_entry `.`; scheduler thread 019ea300-00db-7e22-bda4-705ce83527ff; worker T6 | Recheck child issues, branch, PR, head SHA, PR metadata, review, hosted checks, issue closeout, and main-branch closeout sync before terminalizing; carrier state is tracking-only. |
