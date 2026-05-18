# WI-775 Plan

## Steps

1. Add an explicit adoption intent vocabulary to `loom_init.py` and wire it into CLI parsing plus intake normalization.
2. Let adoption intent influence the current recommendation only enough to support #775: read-only intents defer writes, attach-only selects deep-existing attach, light-governance selects lightweight/minimal paths, and execution-control/strong-governance selects full-bootstrap.
3. Extend bootstrap output with adoption intent, detected repository mode, planned writes, intentionally absent targets, and risk summary.
4. Fail closed when a write would create full-bootstrap execution-control carriers and the user did not explicitly request that intent.
5. Update `loom_check` fixtures for attach-only, ambiguous full-bootstrap block, and explicit execution-control write behavior.
6. Update source skill docs/contracts, regenerate generated skill surfaces, and refresh `examples/new-project`.
7. Validate with syntax checks, targeted adoption fixtures, `make skills-check`, and `python3 tools/loom_check.py .`.

## Validation

- `python3 -m py_compile tools/loom_init.py tools/loom_check.py skills/shared/scripts/loom_init.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_check.py`
- `make skills-check`
- Targeted temporary fixture covering observe-only, attach-only, ambiguous full-bootstrap block, and explicit execution-control write.
- `python3 tools/loom_init.py verify --target examples/new-project`
- `python3 tools/loom_check.py .`
