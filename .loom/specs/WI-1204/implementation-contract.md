# WI-1204 Implementation Contract

## Ownership

- Code ownership: `tools/loom.py`, `tools/check_cli_contract.py`, `tools/check_release_surface.py`, and generated skills check assertions.
- Documentation ownership: README, Codex install docs, unified install docs, host adapter matrix, installed-state v2, and skills README surfaces.
- Fixture ownership: temporary downstream plugin layout fixtures inside contract checks only.

## Exclusions

- Do not change #1196 Codex workstation registration semantics.
- Do not write Codex Desktop user registration state into target repository truth.
- Do not revive `@mc-and-his-agents/loom-installer` as a primary install path.
- Do not delete or overwrite downstream target-owned non-Loom `skills/`.

## Validation

- Required local checks: `make loom-check`; `python3 tools/check_cli_contract.py`; `python3 tools/check_release_surface.py`; `python3 tools/skills_surface.py check`; fixture install/verify/installed-state/doctor/repair-plan commands; docs checks; `git diff --check`.
- Required remote checks: PR checks, target branch validation, and issue closeout evidence.
