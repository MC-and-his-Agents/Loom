# WI-777 Implementation Contract

## Expected Changes

- Source runtime changes belong in `src/skills/shared/scripts/loom_init.py` and `src/skills/shared/scripts/loom_check.py`.
- User-facing source truth belongs in `src/skills/loom-init/**`; generated skill surfaces must be produced by `tools/skills_surface.py generate`.
- Decision prompt output must remain a bootstrap/adoption contract, not a repo-specific policy system.

## Safety Rules

- Classification may inform the recommendation but must not silently authorize heavy writes.
- Attach-only must continue to protect repo-owned truth and forbidden authored carriers.
- Execution-control remains allowed only when explicit intent authorizes it.
- Generated files must not be hand-edited without updating source truth.
