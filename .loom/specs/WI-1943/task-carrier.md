# WI-1943 Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1943 | open | in_progress | primary | .loom/work-items/WI-1943.md | .loom/specs/WI-1943/plan.md#phases | .loom/specs/WI-1943/spec.md#key-scenarios | .loom/specs/WI-1943/plan.md#validation | .loom/specs/WI-1943/evidence-map.md | Work Item issue for terminal closeout carrier gate consumption. | Recheck before review, merge-ready, and closeout. |
| github_issue | https://github.com/MC-and-his-Agents/Loom/pull/1944 | open | in_progress | evidence_locator | .loom/work-items/WI-1943.md | .loom/specs/WI-1943/plan.md#phases | .loom/specs/WI-1943/spec.md#key-scenarios | .loom/specs/WI-1943/plan.md#validation | .loom/specs/WI-1943/evidence-map.md | PR carrying the WI-1943 fix and carrier evidence. | Recheck after PR head or metadata changes. |

## Carrier Boundary

Task carrier state is tracking-only. GitHub issue or PR state does not replace behavior evidence, test evidence, review, merge-ready, or closeout truth.
