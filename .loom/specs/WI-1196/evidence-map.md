# WI-1196 Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-1196-001 | behavior_evidence | tools/loom.py | .loom/specs/WI-1196/spec.md S1-S3 / AC-1 | WI-1196 CLI behavior | present | target payload and workstation registration behavior only | Re-run focused fixture smokes after CLI behavior changes. |
| EV-1196-002 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1196/spec.md AC-1 AC-3 | WI-1196 HotCP-style regression fixture | present | CLI contract evidence only | Re-run python3 tools/check_cli_contract.py after CLI or fixture changes. |
| EV-1196-003 | test_evidence | tools/check_release_surface.py | .loom/specs/WI-1196/spec.md AC-2 | WI-1196 release surface | present | release surface evidence only | Re-run python3 tools/check_release_surface.py after docs or command surface changes. |
| EV-1196-004 | behavior_evidence | README.md | .loom/specs/WI-1196/spec.md AC-2 | WI-1196 adoption docs | present | docs wording evidence only | Re-run docs link check and release surface check after docs edits. |
| EV-1196-005 | fresh_verification_input | .loom/progress/WI-1196.md | EV-1196-001 EV-1196-002 EV-1196-003 EV-1196-004 | WI-1196 latest validation summary | present | merge-ready and issue closeout evidence | Refresh progress summary after final validation, PR merge, and target branch checks. |
