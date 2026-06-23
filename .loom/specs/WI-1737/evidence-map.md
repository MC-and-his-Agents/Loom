# Evidence Map

- Suite path: minimal.

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-1737/spec.md S1 S2 | WI-1737 / canonical checkpoint write behavior / branch work/1737-canonical-checkpoint | present | review / merge-ready / PR gate | Re-run after checkpoint normalization, recovery write, or fixture generation changes. |
| EV-002 | test_evidence | test/checkpoint_canonicalization_test.py | .loom/specs/WI-1737/spec.md S1 S2 | WI-1737 / checkpoint canonicalization tests / branch work/1737-canonical-checkpoint | present | review / merge-ready / PR gate | Re-run after checkpoint normalization, recovery write, or fixture generation changes. |
| EV-003 | test_evidence | tools/check_demo_bootstrap_fixture.py | .loom/specs/WI-1737/spec.md S3 | WI-1737 / demo bootstrap fixture canonical checkpoint values / branch work/1737-canonical-checkpoint | present | review / merge-ready / PR gate | Regenerate or refresh fixture and re-run after generated Loom fixture changes. |
| EV-004 | compatibility_evidence | test/retained_item_lookup_test.py | .loom/specs/WI-1737/implementation-contract.md compatibility | WI-1737 / read compatibility / branch work/1737-canonical-checkpoint | present | review / merge-ready / PR gate | Re-run when retained lookup or checkpoint enum helpers change. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1737.md | EV-001 EV-002 EV-003 EV-004 | WI-1737 / latest validation summary / branch work/1737-canonical-checkpoint | present | merge-ready / PR gate / closeout / status | Refresh latest validation summary, PR body machine carrier, and review record after every non-carrier PR head change. |
