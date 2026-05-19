# WI-784 Plan

## Steps

1. Add a single attach-only forbidden carrier vocabulary to `loom_init.py`.
2. Expose `required_carriers` and `forbidden_authored_carriers` in bootstrap output and `scaffold_profile`.
3. Add attach-only host truth locators to generated `repo-interface.json`.
4. Make attach-only verify scan `init-result`, `planned_writes`, manifest artifacts, write touched paths, and filesystem paths.
5. Guard attach-only writes before scaffold files are materialized.
6. Extend deep-existing bootstrap checks with dry-run assertions, forbidden file poison fixtures, forbidden declaration poison fixtures, and execution-control regression checks.
7. Update adoption and skill output contracts, then regenerate checked-in skill surfaces.
8. Validate with targeted fixtures, `make skills-check`, `make loom-check`, and repo adoption verify.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_check.py src/skills/shared/scripts/governance_surface.py`
- Source and generated attach-only dry-run/write/verify temporary fixtures.
- Source and generated attach-only poison verify temporary fixtures.
- `python3 tools/skills_surface.py check`
- `make skills-check`
- `make loom-check`
- `python3 tools/loom_flow.py adopt verify --target . --item WI-784`
