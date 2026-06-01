# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-877/spec.md acceptance 1, 2, and 5 | WI-877 / work/877-pr-metadata-parser-preflight / PR pending | present | review / merge-ready / closeout / status | Re-run focused rg after parser preflight flow consumption changes. |
| EV-002 | test_evidence | src/skills/shared/scripts/loom_check.py | .loom/specs/WI-877/plan.md validation mapping | WI-877 / parser preflight fixture / current validation summary | present | review / merge-ready / closeout / status | Re-run python3 tools/loom_check.py --profile source --source-surface contract-only . after parser or fixture changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-877.md | EV-001 EV-002 plus git diff --check, skills_surface check, and CLI contract checks | WI-877 / latest validation summary / PR pending | present | merge-ready / closeout / status | Refresh progress summary after final validation, PR creation, or head changes. |
