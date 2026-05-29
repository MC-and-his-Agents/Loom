# Implementation Contract

## Owned Change Surface

- `tools/check_cli_contract.py`
- `src/skills/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_check.py`
- generated skill runtime copies under `skills/*/.loom-runtime/shared/scripts/loom_check.py`
- `.loom/bin/loom_check.py`
- `examples/new-project/.loom/bin/loom_check.py`
- `.loom/work-items/WI-1152.md`
- `.loom/progress/WI-1152.md`
- `.loom/specs/WI-1152/*`

## Contract

- Generated skills parity validation must consume `loom skills check --target . --json` and `tools/skills_surface.py check`.
- Stable source/generated parity must include route matrix, shared references, registry, install layout, upgrade contract, and distribution contract files.
- Per-skill generated `.loom-runtime` parity must include route matrix, registry, and install layout.
- CLI output remains evidence only and must not replace Work Item, review, merge-ready, closeout, Project, or docs/source truth.
- #1152 must not implement stale host conflict, scaffold mutation, PR gate, merge-ready, closeout, Project reconciliation, #1145 closeout, or #1107 closeout fixtures.
