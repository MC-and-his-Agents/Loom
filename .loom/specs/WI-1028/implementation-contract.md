# WI-1028 Implementation Contract

## Owns

- Skills route matrix planning boundary.
- `loom-init` planning routing instructions.
- `loom-story` planning handoff instructions.
- Skills README planning control-plane note.
- Generated skills surface sync.
- WI-1028 Loom carriers.

## Excludes

- Delivery planning methodology changes.
- Issue-tree-plan template changes.
- PR slicing strategy changes.
- GitHub profile mapping changes.
- CLI command implementation.
- GitHub issue/project mutation automation.

## Verification

- `git diff --check`
- focused `rg` for planning routing language
- `python3 .loom/bin/loom_init.py verify --target .`
- `python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1028 --write`
- `python3 tools/skills_surface.py check`
- `python3 tools/check_npm_package.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_release_surface.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
