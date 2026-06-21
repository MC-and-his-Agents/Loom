# WI-1678 Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1678 | Issue open / PR open / branch active before controlled merge | in_progress | primary | .loom/work-items/WI-1678.md | .loom/work-items/WI-1678.md#static-facts | .loom/specs/WI-1678/spec.md | .loom/specs/WI-1678/spec.md | .loom/specs/WI-1678/evidence-map.md | branch work/1678-agent-install-prompt; PR #1679; README documentation-only iteration; carrier status is tracking-only | Recheck issue state, PR head, PR body metadata, hosted checks, controlled merge result, and closeout evidence before changing this carrier to terminal. |
