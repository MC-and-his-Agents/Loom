# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | VERSION | .loom/specs/WI-1203/spec.md AC-1 | WI-1203 / version metadata / current release-bump validation object | present | review / merge-ready / closeout | Re-run `python3 tools/version_surface_check.py` after version metadata changes. |
| EV-002 | test_evidence | .loom/progress/WI-1203.md | .loom/specs/WI-1203/plan.md AC-1 AC-2 | WI-1203 / release checks / current release-bump validation object | present | review / merge-ready / closeout | Re-run release, npm package, CLI contract, and diff checks before PR handoff. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1203.md | EV-001 EV-002 | WI-1203 / latest validation summary / current release-bump validation object | present | merge-ready / closeout | Refresh WI-1203 progress after final branch validation, PR checks, and main release workflow readback. |
