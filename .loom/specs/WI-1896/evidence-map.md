# WI-1896 Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
|---|---|---|---|---|---|---|---|
| EV-001 | behavior_evidence | `tools/loom.py` | S1 S2 S3 / A1 A2 A3 A4 | workstation registry fail-closed classification | present | review / PR gate / closeout | Recheck after workstation registry behavior changes. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py --surface workstation-registry` | S1 S2 S3 / A1 A2 A3 A4 | temp HOME registry fixtures | present | review / PR gate | Rerun after CLI or fixture edits. |
| EV-003 | test_evidence | `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py` | A4 | Python syntax/readability | present | hosted checks | Rerun after Python edits. |
| EV-004 | test_evidence | `git diff --check` | S1-S3 / A1-A5 | diff hygiene | present | review / PR gate | Rerun after any file edit. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1896.md` | EV-001 EV-002 EV-003 EV-004 / A1-A5 | current branch / current head / WI-1896 | present | review / merge-ready / closeout | Refresh after validation, PR metadata, review, hosted checks, merge, or closeout evidence changes. |
