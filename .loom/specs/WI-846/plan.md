# WI-846 Plan

## Steps

1. Add a derived Governance Lint status builder for flow surfaces, reusing the existing lint status/result schemas.
2. Wire `flow pre-review` to consume fact-chain blocking failures and pre-review repo companion requirements through a `governance-lint` deterministic step.
3. Keep absent pre-review repo companion requirements advisory/no-op so adopted repositories are not forced to declare optional pre-review surfaces.
4. Extend `loom_check.py` to require the pre-review lint section and to test stale derived status as a pre-review blocking lint fixture.
5. Regenerate the checked-in skills runtime surface.
6. Validate with py_compile, focused pre-review positive/negative smoke, skills surface check, and full `tools/loom_check.py` before PR readiness.

## Evidence Plan

- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py flow pre-review --target examples/new-project --item INIT-0001`
- stale derived status pre-review negative fixture smoke
- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-846`
- deterministic PR readiness checks before any semantic review

## Rollback

Revert the `flow pre-review` governance_lint wiring, `loom_check.py` contract/negative fixture additions, generated skills surface, and WI-846 carriers, then rerun the focused pre-review smoke and skills surface check.
