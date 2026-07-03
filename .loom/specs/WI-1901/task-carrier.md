# WI-1901 Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1901 | open | in_progress | primary | .loom/work-items/WI-1901.md | .loom/specs/WI-1901/plan.md#phases | .loom/specs/WI-1901/spec.md#key-scenarios | .loom/specs/WI-1901/plan.md#validation | .loom/specs/WI-1901/evidence-map.md | Work Item issue for cache-absent gate validation. | Recheck before review, merge-ready, and closeout. |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1897 | open | in_progress | evidence_locator | .loom/work-items/WI-1901.md | .loom/specs/WI-1901/plan.md#dependencies | .loom/specs/WI-1901/spec.md#scope | .loom/specs/WI-1901/plan.md#dependencies | .loom/specs/WI-1901/evidence-map.md | Parent FR for Global Runtime Cache Store. | Recheck if FR #1897 scope changes. |

## Carrier Boundary

Task carrier state is tracking-only. GitHub issue or Project state does not replace behavior evidence, test evidence, review, merge-ready, or closeout truth.
