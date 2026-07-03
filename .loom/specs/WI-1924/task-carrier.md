# WI-1924 Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1924 | open | in_progress | primary | .loom/work-items/WI-1924.md | .loom/specs/WI-1924/plan.md#steps | .loom/specs/WI-1924/spec.md#scenarios | .loom/specs/WI-1924/plan.md#steps | .loom/specs/WI-1924/evidence-map.md | Work Item issue for closeout role gate repair. | Recheck before review, merge-ready, and closeout. |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1895 | closed | done | evidence_locator | .loom/work-items/WI-1924.md | .loom/specs/WI-1924/plan.md#dependencies | .loom/specs/WI-1924/spec.md#scenarios | .loom/specs/WI-1924/plan.md#dependencies | .loom/specs/WI-1924/evidence-map.md | Regression was discovered while repairing WI-1895 closeout status. | Recheck WI-1895 closeout status after this fix. |
