# WI-1137 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1137.md
- FR / parent locator: #1136
- Scope: doctor declared suite command support and command matrix drift only.
- Suite path: minimal
- Current `HEAD`: branch `work/1137-suite-doctor`
- PR locator: pending until PR is opened; recheck before merge-ready.
- Host state locator: #1137 / Project `Loom` In Progress.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1137/spec.md | required | authored from #1137 | Recheck when doctor scope changes. |
| `plan.md` | .loom/specs/WI-1137/plan.md | required | authored from #1137 | Recheck when validation strategy changes. |
| installed-state contract | docs/adoption/loom-installed-state-v2.md | required | #1137 implementation | Recheck when declared support shape changes. |
| full suite CLI surface | docs/methodology/harness/full-spec-suite-cli-surface.md | required | #1052 / #1137 | Recheck when doctor starts enforcing deeper validators. |
| command matrix | `loom help --json` / tools/loom.py | required | source CLI | Recheck when suite command names or statuses change. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/loom.py | .loom/specs/WI-1137/spec.md S1-S3 | WI-1137 / doctor declared support / current branch | present | doctor diagnostics only | Re-run doctor and CLI contract fixtures after changing declared support parsing. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1137/plan.md validation commands | WI-1137 / CLI contract fixtures | present | doctor diagnostics only | Re-run `python3 tools/check_cli_contract.py`. |
| EV-003 | behavior_evidence | docs/adoption/loom-installed-state-v2.md | .loom/specs/WI-1137/spec.md A6 | WI-1137 / declared support docs | present | docs/source truth only | Recheck docs if installed-state shape changes. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1137.md | EV-001 EV-002 EV-003 | WI-1137 / latest validation summary | present | review / merge-ready / closeout evidence | Refresh progress summary after final validation. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| full suite validators from doctor | deferred | #1137 only checks declared command support and help matrix drift. | verify/profile and suite validators | #1138 changes verify requirements or doctor scope expands. | #1138 |
| scenario skill consumption | deferred | Owned by #1140. | scenario skills | #1140 starts. | #1140 |
