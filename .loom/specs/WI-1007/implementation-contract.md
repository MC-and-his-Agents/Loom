# WI-1007 Implementation Contract

## File Ownership

- `tools/check_release_surface.py`: release-surface negative enforcement and required Codex install wording.
- `tools/loom.py`: `skills release-check` check chain and structured release authority output.
- `tools/check_cli_contract.py`: CLI contract assertions for release authority.
- `packages/loom-installer/package.json`: package-local release check wiring.
- `packages/loom-installer/scripts/check-doc-sync.mjs`: doc-sync needle for Codex default path.
- `.loom/` WI-1007 carriers: record only this work item and validation evidence.

## Acceptance Checks

- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_cli_contract.py`
- `npm --prefix packages/loom-installer run check:docs`
- `npm --prefix packages/loom-installer run check:versions`
- `npm --prefix packages/loom-installer run check:payload`
- `npm --prefix packages/loom-installer run check:distribution`
- `npm --prefix packages/loom-installer run check:release`
- `make check`
- `python3 .loom/bin/loom_flow.py shadow-parity --target .`
- `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1007`

## Release Evidence

This work item must not publish `loom`, publish or deprecate `@mc-and-his-agents/loom-installer`, create a `v*` tag, or create a `loom-installer-v*` tag.
