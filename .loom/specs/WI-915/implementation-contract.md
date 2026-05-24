# WI-915 Implementation Contract

## Command Semantics

- Adoption/profile commands are CLI wrappers; `loom adopt verify` verifies adoption contracts, while bootstrap remains under `loom init bootstrap`.
- `loom profile upgrade` remains dry-run by default through the underlying governance profile runtime and requires explicit apply semantics there.
- `loom gate merge` checks host merge readiness through controlled-merge check; it does not execute merge.
- `loom gate closeout` checks closeout state; it does not sync or close host objects.

## Verification

- `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py`
- `python3 tools/loom.py profile status --target . --json`
- `python3 tools/loom.py checkpoint admission --target . --item WI-915 --json`
- `python3 tools/loom.py gate pr --target . --item WI-915 --json`
- `python3 .loom/bin/loom_init.py fact-chain --target .`
- `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-915`
- `python3 .loom/bin/loom_flow.py shadow-parity --target .`
