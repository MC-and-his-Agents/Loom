# WI-2062 Evidence Map

## Context

- Work Item: WI-2062
- Host issue: https://github.com/MC-and-his-Agents/Loom/issues/2062
- Branch: work/2062-hosted-pr-gate-nonblocking-blockers
- Suite path: minimal

## Evidence Rows

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | Core #273, App #281, Harbor #253 blocker-text comparison and WI-2062 acceptance criteria | work_item=WI-2062; scope=checkpoint-blocker-classification | present | review / merge-ready / PR gate | Recheck after checkpoint or blocker parsing changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | Core/App clear shapes and real/ambiguous blocker shapes | work_item=WI-2062; branch=work/2062-hosted-pr-gate-nonblocking-blockers | present | review / merge-ready / hosted checks | Rerun governance-closeout surface after source or test changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-2062.md | EV-001 EV-002 current validation summary and product head | work_item=WI-2062; head_sha=current PR head at review time | present | semantic review / merge-ready | Mark stale after implementation, validation-summary, or reviewed-head changes. |
