# WI-1203 Implementation Contract

## Ownership

- Allowed: `VERSION`, `package.json`, `skills/*/loom-package.json`, `.loom/work-items/WI-1203.md`, `.loom/progress/WI-1203.md`, `.loom/progress/WI-1196.md`, `.loom/reviews/WI-1203.json`, `.loom/reviews/WI-1203.spec.json`, `.loom/status/current.md`, `.loom/bootstrap/init-result.json`, `.loom/specs/WI-1203/*`, and closeout evidence.
- Forbidden: #1204 downstream plugin layout changes, workstation registration behavior changes, command naming changes, user-level Codex configuration semantics, and target repository layout migrations.

## Validation

- `python3 tools/version_surface_check.py`
- `python3 tools/check_release_surface.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/check_cli_contract.py`
- `git diff --check`
- PR and main branch release workflow readback
