# WI-1896 Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1896 | open | in_progress | primary | .loom/work-items/WI-1896.md | .loom/specs/WI-1896/plan.md#phases | .loom/specs/WI-1896/spec.md#key-scenarios | .loom/specs/WI-1896/plan.md#validation | .loom/specs/WI-1896/evidence-map.md | Work Item issue for workstation registry fail-closed validation. | Recheck before review, merge-ready, and closeout. |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1895 | closed | done | evidence_locator | .loom/work-items/WI-1896.md | .loom/specs/WI-1896/plan.md#dependencies | .loom/specs/WI-1896/spec.md#scope | .loom/specs/WI-1896/plan.md#dependencies | .loom/specs/WI-1896/evidence-map.md | WI-1895 introduced the workstation registry CLI that WI-1896 hardens. | Recheck if #1895 registry command semantics change. |
