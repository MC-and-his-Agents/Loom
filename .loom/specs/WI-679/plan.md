# WI-679 Plan

## Steps

- Document the context pack and repeated blocker signal contracts in `review-execution.md`.
- Build context pack evidence from the current review record and prior normalized findings.
- Add context pack locator to engine evidence, metadata, and `review_record_input`.
- Include recent findings and repeated blocker guidance in the default review prompt.
- Add fixtures for context pack presence and repeated blocker/root-cause candidate detection.
- Refresh generated skill surfaces and demo bootstrap output.
- Run targeted checks and full `make check`.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py`
- `make check`
