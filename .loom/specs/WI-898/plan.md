# WI-898 Plan

## Implementation Steps

1. Replace the repo-local `tools/loom.py` wrapper with a CLI-first router that exposes `version`, `help`, and `installed-state show|validate|export`.
2. Keep existing scenario/status commands as delegated compatibility routes.
3. Register the full #885 command matrix as reserved/delegated/implemented and make reserved commands fail closed with structured JSON.
4. Add `loom-installed-state/v2` validation for schema, layer version context, runtime state, upgrade eligibility, failed layer metadata, and installation graph ids.
5. Add `tools/check_cli_contract.py` and wire it into `make check`.
6. Add harness/adoption docs that freeze authority boundaries, command naming, JSON fields, fail-closed behavior, fallback semantics, installed-state schema, and graph semantics.

## Validation

- `python3 tools/loom.py version --json`
- `python3 tools/loom.py installed-state validate --target examples/new-project --json`
- `make cli-contract-check`
- `make check`

## Risk Controls

- Reserved commands must block instead of pretending later FRs are complete.
- Installed-state must not infer validity from legacy files alone.
- Validation fixtures use temporary directories and leave no repository residue.
