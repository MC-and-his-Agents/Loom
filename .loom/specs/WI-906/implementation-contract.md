# WI-906 Implementation Contract

## Owned Files

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/cli-command-matrix.md`
- `docs/methodology/harness/cli-first-control-plane.md`
- `docs/adoption/loom-installed-state-v2.md`
- `.loom/work-items/WI-906.md`
- `.loom/progress/WI-906.md`
- `.loom/reviews/WI-906.json`
- `.loom/status/current.md`

## Required Evidence

- `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py`
- `python3 tools/loom.py detect --target . --json`
- `make check`

## Non-Goals

- No mutating repair apply.
- No installer shim implementation.
- No host adapter install/upgrade/remove implementation.
- No skills generation/sync/package/release-check implementation.
- No import of WebEnvoy, Syvert, or HotCP repo-specific governance rules.
