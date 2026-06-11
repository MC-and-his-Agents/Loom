# WI-1243 Execution Breakdown

| Unit | Scope | Owner | Status | Validation |
| --- | --- | --- | --- | --- |
| unit-runtime-carrier-plan | Deterministic repair/upgrade plan for retained `.loom/bin` under `global-cli`. | Loom #1243 worker | done | `git diff --check`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 -m py_compile tools/loom.py tools/check_cli_contract.py` |
