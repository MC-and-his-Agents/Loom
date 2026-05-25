# WI-1008 Implementation Contract

## File Ownership

- `.github/workflows/loom-cli-release.yml`: main-push auto publish, dispatch repair, tag collision, and no-publish PR behavior.
- `docs/adoption/loom-cli-release-surface.md`: authoritative release-surface semantics for #1008.
- `tools/check_release_surface.py`: static guard needles for auto publish and tag-collision semantics.
- `.loom/` WI-1008 carriers: record only this work item and validation evidence.

## Acceptance Checks

- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_cli_contract.py`
- `ruby -e "require 'yaml'; YAML.load_file('.github/workflows/loom-cli-release.yml')"`
- `npm --prefix packages/loom-installer run check:release`
- `python3 .loom/bin/loom_flow.py shadow-parity --target .`
- `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1008`
- `make check`

## Release Evidence

This work item must not create a `v*` tag, create a GitHub Release, publish or deprecate `@mc-and-his-agents/loom-installer`, or create a `loom-installer-v*` tag. First actual `loom` CLI release evidence belongs to #1009.
