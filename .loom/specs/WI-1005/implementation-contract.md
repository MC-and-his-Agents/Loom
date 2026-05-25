# WI-1005 Implementation Contract

## File Ownership

- `.github/workflows/node-installer-release.yml`: sunset the installer release workflow without changing unrelated workflows.
- `tools/check_release_surface.py`: add guardrails for the sunset workflow state.
- `.loom/` WI-1005 carriers: record only this work item and validation evidence.

## Acceptance Checks

- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_cli_contract.py`
- `npm --prefix packages/loom-installer run check:docs`
- `npm --prefix packages/loom-installer run check:versions`
- `npm --prefix packages/loom-installer run check:payload`
- `npm --prefix packages/loom-installer run check:distribution`
- Ruby YAML parse for `.github/workflows/*.yml`
- `make check`
- `python3 .loom/bin/loom_flow.py shadow-parity --target .`
- `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1005`

## Release Evidence

This work item must not publish `@mc-and-his-agents/loom-installer`, must not create a `loom-installer-v*` tag, and must not create an installer GitHub Release.
