# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-874/spec.md acceptance 1, 2, 3, and 5 | WI-874 / work/874-pr-body-render-edit-preflight / PR pending | present | pre-review / review / merge-ready / closeout / status | Re-run focused rg after body artifact preflight changes. |
| EV-002 | test_evidence | src/skills/shared/scripts/loom_check.py | .loom/specs/WI-874/plan.md validation mapping | WI-874 / body-file preflight fixture / current validation summary | present | review / merge-ready / closeout / status | Re-run python3 tools/loom_check.py --profile source --source-surface contract-only . after parser or fixture changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-874.md | EV-001 EV-002 plus git diff --check, skills_surface check, PR #1193 body-file/readback preflight, loom_check, CLI contract, release/version/package surface checks, and suite validation | WI-874 / latest validation summary / PR #1193 | present | merge-ready / closeout / status | Refresh progress summary after final validation, PR creation, or head changes. |
