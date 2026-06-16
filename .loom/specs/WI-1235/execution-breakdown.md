# Execution Breakdown

## Contract

- Schema marker: loom-execution-breakdown/v1
- Work Item locator: .loom/work-items/WI-1235.md
- Plan locator: .loom/specs/WI-1235/plan.md
- Scope: #1235 safe repair/sync flow only.
- Freshness rule: Recheck after code, generated runtime, test, carrier, PR head, or review changes.

## Units

| unit_id | unit_title | unit_goal | unit_scope | non_goals | source_mapping | carrier_mapping | owner_expectation | status | provenance | freshness_rule | consumer_contract |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U1 | Shared repair runtime | Add host-complete active carrier repair plan/apply behavior. | `src/skills/shared/scripts/loom_flow.py`; generated runtime copies | host mutation, #1236/#1237/#1296 | S1-S3; Phase 1 | .loom/specs/WI-1235/task-carrier.md | main Codex agent | done | issue #1235; local validation | rerun governance-closeout after changes | review, merge-ready, closeout consume EV-001/EV-002 |
| U2 | Root CLI integration | Expose safe root `loom repair plan/apply` semantics and block mixed action apply. | `tools/loom.py` | installed-surface mutating repair | S1-S3; Phase 2 | .loom/specs/WI-1235/task-carrier.md | main Codex agent | done | read-only review finding P2 | rerun aggregate after changes | review, merge-ready, closeout consume EV-001/EV-003 |
| U3 | Regression evidence | Add focused fixtures for plan/apply/fail-closed behavior and generated drift. | `tools/check_cli_contract.py` | full #1236 fixture inventory | A1-A4; Phase 3 | .loom/specs/WI-1235/task-carrier.md | main Codex agent | done | issue #1235 acceptance criteria | rerun governance-closeout and aggregate after changes | review, merge-ready, closeout consume EV-002/EV-003 |
| U4 | Carrier/review readiness | Bind WI-1235 fact-chain, suite, status, and shadow evidence to the PR. | `.loom/**` WI-1235 carriers | terminal closeout before merge | A5; Phase 3 | .loom/specs/WI-1235/task-carrier.md | main Codex agent | in_progress | current Codex thread | refresh after commit/PR/review/gate changes | review and merge-ready consume carrier/shadow/review |

## Deferred Units

| unit_id | locator | reason | activation_condition | does_not_currently_block |
| --- | --- | --- | --- | --- |
| D1 | GitHub issue #1236 | fixture inventory consumes #1235 stable behavior | #1235 merged and closed | #1235 PR |
| D2 | GitHub issue #1237 | docs outline consumes #1235 stable behavior | #1235 merged and closed | #1235 PR |
| D3 | GitHub issue #1296 | release/no-release closeout runs after #1236/#1237 | #1236 and #1237 merged and closed | #1235 PR |

## Forbidden Use

- Task carrier `done`, Project `Done`, PR merged, or issue closed does not replace Work Item/recovery/review/merge-ready/closeout truth.
- This file does not author dynamic recovery fields.

