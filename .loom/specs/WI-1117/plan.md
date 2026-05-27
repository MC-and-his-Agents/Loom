# WI-1117 Plan

## Implementation Plan

1. Extend `tools/check_cli_contract.py` scaffold fixtures with explicit audit-field assertions.
2. Keep `tools/loom.py` behavior unchanged unless the assertions expose a contract gap.
3. Run focused scaffold JSON validation and source-surface checks.
4. Record spec and implementation reviews after validation passes.

## Validation Plan

- `python3 tools/check_cli_contract.py`
- targeted `loom suite scaffold` dry-run/apply smoke for minimal and full suites if needed
- `git diff --check`
- focused `rg` for scaffold JSON audit fields and forbidden surfaces
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1117`

## Out Of Scope

- No rollback execution command.
- No new scaffold artifacts.
- No host, review, merge-ready, closeout, generated skill, `/speckit.*`, or `.specify/` mutation surfaces.
