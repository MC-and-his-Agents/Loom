# WI-1790 Task Carrier

| Carrier Type | Carrier Locator | Source Value | Normalized Status | Relationship | Work Item Locator | Breakdown Unit Locator | Spec Scenario Locator | Plan Phase Locator | Validation Strategy Locator | Provenance | Freshness Rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| external_tracker | https://github.com/MC-and-his-Agents/Loom/pull/1790 | Fix installed package `loom init bootstrap --target ... --json` entrypoint and publish v0.21.1 | in_progress | primary | .loom/work-items/WI-1790.md | .loom/specs/WI-1790/plan.md#phases | .loom/specs/WI-1790/spec.md#scenarios | .loom/specs/WI-1790/plan.md#validation | .loom/specs/WI-1790/evidence-map.md | User-reported installed CLI failure; branch work/fix-init-bootstrap-entrypoint; PR #1790. | Recheck PR head, hosted checks, release judgment, npm publish, plugin payload refresh, and installed CLI smoke before closeout. |
