# Evidence Map

- Suite path: minimal.

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | skills/shared/scripts/loom_flow.py | .loom/specs/WI-1740/spec.md S1 S2 S3 | WI-1740 / review freshness classification / branch work/1740-review-freshness | present | review / merge-ready / PR gate | Re-run after review binding, semantic disposition, approval lint, retained PR gate, or closeout backlink logic changes. |
| EV-002 | generated_runtime_evidence | src/skills/shared/scripts/loom_flow.py | EV-001 | WI-1740 / source skill runtime copy | present | hosted checks / carrier refresh / generated surface check | Re-run py_compile and skills surface checks after runtime copy changes. |
| EV-003 | generated_runtime_evidence | .loom/bin/loom_flow.py | EV-001 EV-002 | WI-1740 / repo-local runtime copy | present | hosted checks / carrier refresh / generated surface check | Re-run carrier refresh after repo-local runtime copy changes. |
| EV-004 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1740/spec.md S1 S2 S3 | WI-1740 / PR metadata fixture group / branch work/1740-review-freshness | present | review / merge-ready / PR gate | Re-run `tools/check_cli_contract.py --fixture-group pr-metadata` after fixture or classifier changes. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1740.md | EV-001 EV-002 EV-003 EV-004 | WI-1740 / latest validation summary / branch work/1740-review-freshness | present | merge-ready / PR gate / closeout / status | Refresh latest validation summary, PR body machine carrier, and review record after every non-carrier PR head change. |
