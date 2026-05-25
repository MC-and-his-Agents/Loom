# WI-1006 Implementation Contract

## File Ownership

- `README.md` and `README.zh-CN.md`: default install and release surface wording.
- `docs/adoption/loom-cli-release-surface.md`, `docs/adoption/version-authority-map.md`, and `docs/adoption/codex-install.md`: authority and install contract wording.
- `packages/loom-installer/README.md` and `packages/loom-installer/README.zh-CN.md`: package-level deprecated legacy wording.
- `packages/loom-installer/scripts/check-doc-sync.mjs`, `tools/check_release_surface.py`, and `tools/version_surface_check.py`: documentation contract needles only.
- `skills/distribution-and-adapter-contract.md` and `src/skills/distribution-and-adapter-contract.md`: installer adapter wording that otherwise conflicts with #1006.
- `.loom/` WI-1006 carriers: record only this work item and validation evidence.

## Acceptance Checks

- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_cli_contract.py`
- `npm --prefix packages/loom-installer run check:docs`
- `npm --prefix packages/loom-installer run check:versions`
- `npm --prefix packages/loom-installer run check:payload`
- `npm --prefix packages/loom-installer run check:distribution`
- `make check`
- `python3 .loom/bin/loom_flow.py shadow-parity --target .`
- `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1006`

## Release Evidence

This work item must not publish `loom`, publish `@mc-and-his-agents/loom-installer`, create a `v*` tag, or create a `loom-installer-v*` tag.
