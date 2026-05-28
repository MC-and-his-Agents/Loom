# WI-1140 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1140.md
- FR / parent locator: #1136
- Scope: scenario skill suite CLI JSON consumption only.
- Suite path: minimal
- Current `HEAD`: branch `work/1140-suite-skills`
- PR locator: pending until PR is opened; recheck before merge-ready.
- Host state locator: #1140 / Project `Loom` In Progress.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1140/spec.md | required | authored from #1140 | Recheck when scenario skill scope changes. |
| `plan.md` | .loom/specs/WI-1140/plan.md | required | authored from #1140 | Recheck when validation strategy changes. |
| route matrix | src/skills/route-matrix.md | required | #1140 implementation | Recheck when scenario routing changes. |
| full suite CLI surface | docs/methodology/harness/full-spec-suite-cli-surface.md | required | #1052 / #1140 | Recheck when suite command consumption changes. |
| generated runtime | skills/shared/scripts/loom_flow.py / .loom/bin/loom_flow.py | required | source skills sync | Recheck after source runtime changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-1140/spec.md S1-S4 | WI-1140 / scenario runtime / current branch | present | scenario gate input evidence only | Re-run scenario flow checks after runtime changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1140/plan.md validation commands | WI-1140 / CLI contract fixtures | present | CLI contract evidence only | Re-run `python3 tools/check_cli_contract.py`. |
| EV-003 | behavior_evidence | src/skills/route-matrix.md | .loom/specs/WI-1140/spec.md A4 | WI-1140 / skill docs boundary | present | docs/source truth only | Re-run `python3 tools/skills_surface.py check`. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1140.md | EV-001 EV-002 EV-003 | WI-1140 / latest validation summary | present | review / merge-ready / closeout evidence | Refresh progress summary after final validation. |
