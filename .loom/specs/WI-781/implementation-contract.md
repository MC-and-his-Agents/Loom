# WI-781 Implementation Contract

## Source Truth

- Edit shared source under `src/skills/shared/scripts/` and `src/skills/shared/references/`.
- Update adoption docs under `docs/adoption/` when the carrier visibility contract changes.
- Regenerate generated skills with `python3 tools/skills_surface.py generate`.
- Refresh `examples/new-project` with the existing demo bootstrap target.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_init.py skills/shared/scripts/loom_check.py tools/loom_init.py tools/loom_check.py`
- Targeted temporary fixture covering `.loom/*` block, `/.loom/*` repair, stable carrier Git visibility, runtime scratch ignore, and later `verify` drift failure.
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py .`
- `make skills-check`
- `make loom-check`

## Closeout Evidence

The issue can close when the PR is merged, issue #781 is closed, and adoption no longer silently succeeds when blanket `.loom` gitignore rules hide stable carriers.
