# WI-780 Implementation Contract

## Source Truth

- Edit shared source under `src/skills/shared/scripts/` and `src/skills/shared/references/`.
- Regenerate generated skills with `python3 tools/skills_surface.py generate`.
- Refresh `examples/new-project` with the existing `tools/loom_init.py bootstrap` command.
- Bump the installer package version when the generated skill/runtime payload behavior changes.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py src/skills/shared/scripts/governance_surface.py`
- Targeted fixtures for execution-control, light-governance, and attach-only adoption.
- `python3 tools/skills_surface.py check`
- `make skills-check`
- `make loom-check`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`

## Closeout Evidence

The issue can close when the PR is merged, issue #780 is closed, and default adoption no longer produces placeholder release target truth.
