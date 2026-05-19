# WI-777 Plan

## Steps

1. Inspect current adoption intent, scaffold profile, and recommendation assembly in `loom_init.py`.
2. Add a structured decision prompt model for ambiguous or divergent adoption choices.
3. Enforce write-time fail-closed behavior for missing intent plus heavy execution-control writes.
4. Add targeted fixtures covering dry-run prompt output, ambiguous choices, explicit execution-control, and fail-closed write behavior.
5. Update `loom-init` source documentation and regenerate skill surfaces.
6. Validate with targeted checks, skills surface checks, demo bootstrap, skills-check, and PR CI.

## Validation Targets

- `python3 -m py_compile src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_check.py`
- targeted decision-prompt fixture through `check_deep_existing_repo_bootstrap`
- `python3 tools/skills_surface.py generate`
- `python3 tools/skills_surface.py check`
- `make loom-demo-new-project`
- `make skills-check`
- `make loom-check` or CI `loom-check` if local long-run blocks
