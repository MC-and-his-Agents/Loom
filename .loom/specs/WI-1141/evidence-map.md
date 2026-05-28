# WI-1141 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1141.md
- FR / parent locator: #1136
- Scope: `loom-review` consumed locator recording only.
- Suite path: minimal
- Current `HEAD`: branch `work/1141-review-consumed-locators`
- PR locator: pending until PR is opened; recheck before merge-ready.
- Host state locator: #1141 / Project `Loom` In Progress.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1141/spec.md | required | authored from #1141 | Recheck when review consumed input semantics change. |
| `plan.md` | .loom/specs/WI-1141/plan.md | required | authored from #1141 | Recheck when validation strategy changes. |
| gate-chain contract | docs/methodology/harness/gate-chain.md | required | #1014-#1020 / #1136 | Recheck when review gate consumed inputs change. |
| evidence-map contract | docs/methodology/templates/evidence-map.md | required | #1018 / #1136 | Recheck when evidence-map consumer boundary changes. |
| consistency-analysis contract | docs/methodology/templates/consistency-analysis.md | required | #1018 / #1136 | Recheck when consistency-analysis locator consumption changes. |
| implementation contract | .loom/specs/WI-1141/implementation-contract.md | required | authored from #1141 | Recheck when runtime ownership or non-goals change. |
| shared runtime | src/skills/shared/scripts/loom_flow.py | required | #1141 implementation | Recheck after review record code changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-1141/spec.md S1-S3 | WI-1141 / review record writer / current branch | present | review record evidence only | Re-run review record contract fixtures after runtime changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1141/plan.md validation commands | WI-1141 / CLI contract fixtures | present | CLI contract evidence only | Re-run `python3 tools/check_cli_contract.py`. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1141.md | EV-001 EV-002 | WI-1141 / latest validation summary | present | review / merge-ready / closeout evidence | Refresh progress summary after final validation. |
