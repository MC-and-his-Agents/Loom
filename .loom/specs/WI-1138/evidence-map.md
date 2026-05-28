# WI-1138 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1138.md
- FR / parent locator: #1136
- Scope: verify/profile suite validation requirement consumption only.
- Suite path: minimal
- Current `HEAD`: branch `work/1138-suite-verify`
- PR locator: pending until PR is opened; recheck before merge-ready.
- Host state locator: #1138 / Project `Loom` In Progress.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1138/spec.md | required | authored from #1138 | Recheck when verify scope changes. |
| `plan.md` | .loom/specs/WI-1138/plan.md | required | authored from #1138 | Recheck when validation strategy changes. |
| installed-state contract | docs/adoption/loom-installed-state-v2.md | required | #1138 implementation | Recheck when profile requirement shape changes. |
| full suite CLI surface | docs/methodology/harness/full-spec-suite-cli-surface.md | required | #1052 / #1138 | Recheck when verify starts enforcing deeper validators. |
| command matrix | `loom help --json` / tools/loom.py | required | source CLI | Recheck when verify command args or suite command status changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/loom.py | .loom/specs/WI-1138/spec.md S1-S4 | WI-1138 / verify suite requirement / current branch | present | verify gate evidence only | Re-run verify fixtures after changing requirement parsing. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1138/plan.md validation commands | WI-1138 / CLI contract fixtures | present | verify gate evidence only | Re-run `python3 tools/check_cli_contract.py`. |
| EV-003 | behavior_evidence | docs/adoption/loom-installed-state-v2.md | .loom/specs/WI-1138/spec.md A7 | WI-1138 / profile requirement docs | present | docs/source truth only | Recheck docs if installed-state shape changes. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1138.md | EV-001 EV-002 EV-003 | WI-1138 / latest validation summary | present | review / merge-ready / closeout evidence | Refresh progress summary after final validation. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| evidence/carrier/consistency validators from verify | deferred | #1138 only gates `suite validate`; later Work Items own review/closeout/reconciliation consumption. | review / closeout / reconciliation | #1141, #1142, or #1143 starts. | #1141 / #1142 / #1143 |
| scenario skill consumption | deferred | Owned by #1140. | scenario skills | #1140 starts. | #1140 |
