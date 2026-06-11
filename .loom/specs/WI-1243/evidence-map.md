# WI-1243 Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-1243-1 | test_evidence | `python3 tools/check_cli_contract.py --surface adoption-host-metadata` | S1 S2 S3 S4 / AC-1 AC-2 AC-3 AC-4 | WI-1243 targeted contract surface | current | worker local validation, review, PR gate | Re-run the adoption-host-metadata surface after changing repair or upgrade planning. |
| EV-1243-2 | structural_evidence | `python3 -m py_compile tools/loom.py tools/check_cli_contract.py` | AC-1 AC-4 | Python syntax for scoped implementation files | current | worker local validation | Re-run compile checks after editing Python sources. |
| EV-1243-3 | structural_evidence | `git diff --check` | AC-1 AC-2 AC-3 AC-4 AC-5 | whitespace / patch cleanliness | current | worker local validation, review | Re-run after any file edit. |
| EV-1243-4 | documentation_evidence | `docs/adoption/loom-installed-state-v2.md`, `docs/adoption/cli-first-legacy-migration-playbook.md` | S5 / AC-5 | runtime-carrier migration semantics | current | review and PR gate context | Re-read docs if migration semantics change. |
