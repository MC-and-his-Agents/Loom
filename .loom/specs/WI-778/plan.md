# WI-778 Plan

## Steps

1. Add a scaffold profile vocabulary and profile selection function to `loom_init.py`.
2. Make `initial_artifacts`, `planned_writes`, `scaffold_target`, and `verify_target` consume the profile boundary.
3. Add `scaffold_profile` and top-level `upgrade_triggers` to bootstrap output.
4. Preserve existing attach-only and execution-control behavior while adding explicit light-governance behavior.
5. Update `loom_check` fixtures for light-governance and execution-control profile assertions.
6. Update source skill docs/contracts, regenerate generated skill surfaces, and refresh `examples/new-project`.
7. Validate with syntax checks, targeted profile fixtures, `make skills-check`, and `python3 tools/loom_check.py .`.

## Validation

- `python3 -m py_compile tools/loom_init.py tools/loom_check.py skills/shared/scripts/loom_init.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- Targeted temporary fixtures covering `light-governance` new/small-existing, `attach-only`, and `execution-control`.
- `make skills-check`
- `python3 tools/loom_init.py verify --target examples/new-project`
- `python3 tools/loom_check.py .`
