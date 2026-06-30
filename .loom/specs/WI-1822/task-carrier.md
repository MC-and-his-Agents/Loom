# Task Carrier

| carrier_type | carrier_locator | source_value | normalized_status | relationship | work_item_locator | breakdown_unit_locator | spec_scenario_locator | plan_phase_locator | validation_strategy_locator | provenance | freshness_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| github_issue | https://github.com/MC-and-his-Agents/Loom/issues/1822 | Issue closed / implementation PR #1823 merged / release PR #1824 merged / v0.22.1 published and read back | done | primary | .loom/work-items/WI-1822.md | .loom/specs/WI-1822/task-carrier.md#fix-scope | .loom/specs/WI-1822/evidence-map.md#evidence-rows | .loom/progress/WI-1822.md | .loom/specs/WI-1822/evidence-map.md | workspace_entry `.`; implementation head `31abfaa65d221655e1dc0a11ebadb9caba6b15e4`; implementation merge `82d9e1867fdb5454b567e0217fcae6d9978db5e6`; release merge `a274c09bb4aeb47d0ce07aca2c290e7965030a75`; issue #1822 closed at 2026-06-30T14:22:38Z | Terminal readback: #1822 closed, PR #1823/#1824 merged, v0.22.1 tag/GitHub Release/npm published, and closeout sync applied. |

## Fix Scope

- Normalize `closeout` checkpoint input to `closed_out` in the shared Loom flow runtime copies.
- Add a focused CLI contract check so future resume/state-check consumption keeps accepting real terminal carrier wording.
