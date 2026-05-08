# WI-675 Plan

## Steps

- Define the review engine profile contract in `docs/methodology/harness/review-execution.md` and synchronized skill references.
- Add deterministic profile resolution to `loom_flow.py`.
- Pass explicit model and reasoning flags to Codex in `review run`.
- Record the resolved profile in engine metadata and `review_record_input`.
- Add review-run fixtures for positive evidence, override evidence, missing override reason, and missing profile metadata.
- Refresh generated skill surfaces.
- Run targeted checks and full `make check`.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py`
- `make check`
