# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | skills/shared/scripts/loom_check.py | .loom/specs/WI-1276/spec.md S1-S3 | WI-1276 / review-run source surface behavior | present | review / merge-ready evidence | Re-run focused and aggregate source-surface checks after `loom_check.py` changes. |
| EV-002 | test_evidence | .loom/progress/WI-1276.md | .loom/specs/WI-1276/spec.md AC-1-AC-5 | WI-1276 / local validation summary | present | review / merge-ready evidence | Refresh validation summary after any head, carrier, or PR metadata change. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1276.md | EV-001 EV-002 | WI-1276 / fresh verification evidence | present | review / merge-ready evidence | Re-run validation and update progress before current-head review. |
