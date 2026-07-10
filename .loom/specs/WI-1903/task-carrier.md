# WI-1903 Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1903 | open | in_progress | primary | .loom/work-items/WI-1903.md | .loom/specs/WI-1903/plan.md#implementation-phases | .loom/specs/WI-1903/spec.md#key-scenarios | .loom/specs/WI-1903/plan.md#validation | .loom/specs/WI-1903/evidence-map.md | Work Item issue for plan-only workstation upgrade command. | Recheck before review, merge-ready, and closeout. |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1902 | open | in_progress | evidence_locator | .loom/work-items/WI-1903.md | .loom/specs/WI-1903/plan.md#constraints | .loom/specs/WI-1903/spec.md#scope | .loom/specs/WI-1903/plan.md#constraints | .loom/specs/WI-1903/evidence-map.md | Parent FR for Workstation Upgrade Orchestrator. | Recheck if FR #1902 scope changes. |

## Carrier Boundary

Task carrier state is tracking-only. GitHub issue or Project state does not replace behavior evidence, test evidence, review, merge-ready, or closeout truth.
