# WI-1118 Plan

## Implementation Plan

1. Add a forbidden truth-surface fixture list to `tools/check_cli_contract.py`.
2. Hash pre-seeded forbidden surfaces before scaffold commands and compare after dry-run/apply.
3. Assert `planned_writes` and `created_locators` stay inside the scaffold artifact whitelist.
4. Keep `tools/loom.py` unchanged unless the negative fixtures expose a behavior gap.
5. Record spec and implementation reviews after validation passes.

## Validation Plan

- `python3 tools/check_cli_contract.py`
- `git diff --check`
- focused `rg` for forbidden truth-surface fixtures and scaffold boundary assertions
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1118`

## Out Of Scope

- No host, review, merge-ready, closeout, generated skill, task-carrier, `/speckit.*`, or `.specify/` write surface.
- No generated skills/reference synchronization.
- No rollback execution command.
