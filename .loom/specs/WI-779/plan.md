# WI-779 Plan

## Steps

1. Remove formal spec suite generation from the `light-governance` artifact set.
2. Keep work item, progress, status, and formal spec carriers in the `execution-control` artifact set.
3. Update `light-governance` dry-run metadata, README rendering, review placeholders, deferred capabilities, and verify checks to treat formal specs as intentionally absent.
4. Update lightweight retrofit and zero-friction adoption docs, then regenerate `skills/` from `src/skills/`.
5. Add `loom_check` fixture assertions for light-governance absence, poisoned spec verify failure, and execution-control preservation.
6. Validate with targeted fixtures plus `skills-check` and `loom-check`.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_check.py`
- targeted #779 dry-run/write/verify fixture
- `python3 tools/skills_surface.py check`
- `make skills-check`
- `make loom-check`
