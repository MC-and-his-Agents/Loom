# WI-816 Plan

## Steps

1. Update closeout gate resolution to prefer repo-declared `make loom-check` and expose gate provenance.
2. Suppress Python bytecode writes in runtime entrypoints and subprocess gates.
3. Treat installed runtime Python cache residue as installer drift.
4. Add story carrier runtime checker and scaffold `.loom/stories/_template.md`.
5. Regenerate skills surfaces and the example adopted repo.
6. Validate generated surfaces, installer behavior, adopted repo closeout, root Loom checks, and cache purity.

## Validation

- `git diff --check`
- `python3 tools/skills_surface.py check`
- `npm --prefix packages/loom-installer test`
- `make -C examples/new-project loom-check`
- `python3 tools/loom_flow.py closeout check --target examples/new-project --owner owner --repo repo`
- `python3 tools/loom_check.py /Users/mc/dev/Loom`
- Python cache `find` scan returns no runtime cache residue.

