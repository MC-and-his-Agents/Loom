# WI-1494 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1494.md
- Host issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1494
- Scope: explicit Work Item binding for closeout and reconciliation runtime commands only.
- Suite path: minimal
- Current branch: work/1494-closeout-item-binding
- PR locator: pending until PR creation; recheck before merge-ready.

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-1494/spec.md S1-S3 | WI-1494 closeout/reconciliation runtime binding | present | #1494 review and merge-ready evidence only | Re-run closeout/reconciliation targeted checks after changing runtime lookup behavior. |
| EV-002 | test_evidence | test/retained_item_lookup_test.py | .loom/specs/WI-1494/plan.md validation commands | WI-1494 retained item lookup fixtures | present | #1494 review and merge-ready evidence only | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 test/retained_item_lookup_test.py`. |
| EV-003 | test_evidence | tools/skills_surface.py | generated runtime parity | WI-1494 generated skill runtime copies | present | generated-tree drift evidence only | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1494.md | EV-001 EV-002 EV-003 | WI-1494 latest validation summary | present | review, PR gate, and merge-ready evidence only | Refresh Latest Validation Summary after final targeted validation or head changes. |
