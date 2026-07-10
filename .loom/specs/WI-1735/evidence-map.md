# WI-1735 Evidence Map

- Suite path: not_applicable.

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | README.md | `loom ship` short diagnostics, dry-run/apply order, auto-repair boundary, generated-only drift boundary, validation profile expectation, and closeout escalation contract | WI-1735 / ship main-path contract docs / branch work/1735-ship-contract | present | review / merge-ready / PR gate / dependent implementation issues | Re-run ship-wrapper contract check after README or ship contract wording changes. |
| EV-002 | behavior_evidence | docs/methodology/harness/cli-command-matrix.md | ship wrapper command matrix and escalation boundary | WI-1735 / CLI command matrix contract / branch work/1735-ship-contract | present | review / merge-ready / PR gate / dependent implementation issues | Re-run ship-wrapper contract check after command matrix changes. |
| EV-003 | test_evidence | tools/check_cli_contract.py | ship-wrapper focused contract expectations | WI-1735 / ship-wrapper contract check / branch work/1735-ship-contract | present | review / merge-ready / PR gate | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper` after contract checker or ship wording changes. |
| EV-004 | fresh_verification_input | .loom/progress/WI-1735.md | EV-001 EV-002 EV-003 | WI-1735 / latest validation summary / branch work/1735-ship-contract | present | merge-ready / PR gate / closeout / dependent issue consumption | Refresh latest validation summary, PR body machine carrier, and review record after every non-carrier PR head change. |
