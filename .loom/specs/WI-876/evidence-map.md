# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | docs/adoption/repo-companion-contract.md | .loom/specs/WI-876/spec.md acceptance 1 and 3 | WI-876 / d8cf29e990b2c893da39e0cea3fb5875789e4f9f / PR #1191 | present | review / merge-ready / closeout / status | Re-run focused rg after carrier contract text changes. |
| EV-002 | test_evidence | tools/skills_surface.py | .loom/specs/WI-876/plan.md validation mapping | WI-876 / generated skills surface / PR #1191 | present | review / merge-ready / closeout / status | Re-run python3 tools/skills_surface.py check after source or generated skills reference changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-876.md | EV-001 EV-002 plus git diff --check and loom_check contract-only | d8cf29e990b2c893da39e0cea3fb5875789e4f9f / validation summary / PR #1191 | present | merge-ready / closeout / status | Refresh progress summary after final validation or head changes. |
