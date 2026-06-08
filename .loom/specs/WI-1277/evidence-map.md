# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | skills/shared/scripts/loom_check.py | .loom/specs/WI-1277/spec.md S1-S3 | WI-1277 / merge-gate source surface behavior | present | review / merge-ready evidence | Re-run focused and aggregate source-surface checks after `loom_check.py` changes. |
| EV-002 | behavior_evidence | src/skills/shared/scripts/loom_check.py | .loom/specs/WI-1277/spec.md AC-1-AC-4 | WI-1277 / canonical source-surface registry | present | generated skills parity / review evidence | Re-run skills generation and skills check after canonical source changes. |
| EV-003 | test_evidence | .loom/progress/WI-1277.md | .loom/specs/WI-1277/spec.md AC-1-AC-5 | WI-1277 / local validation summary | present | review / merge-ready evidence | Refresh validation summary after any head, carrier, or PR metadata change. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1277.md | EV-001 EV-003 | WI-1277 / fresh verification evidence | present | review / merge-ready evidence | Re-run validation and update progress before current-head review. |
