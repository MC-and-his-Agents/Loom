# WI-987 Implementation Contract

## Owned Paths

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/shared/references/harness/closeout-gate.md`
- `docs/methodology/harness/closeout-gate.md`
- `skills/**`
- `examples/new-project/.loom/**`
- `.loom/work-items/WI-987.md`
- `.loom/progress/WI-987.md`
- `.loom/reviews/WI-987*.json`
- `.loom/specs/WI-987/**`
- `.loom/status/current.md`
- `.loom/shadow/*.json`

## Required Validation

- `python3 tools/skills_surface.py check`
- `make py-compile`
- `python3 tools/loom_check.py`
- `make check`
- `python3 tools/loom_flow.py closeout check --target . --issue 835 --pr 984 --branch work/835-complex-existing-authority-migration --owner MC-and-his-Agents --repo Loom`

## Merge Contract

- PR body must bind `Loom Work Item: WI-987`.
- PR body must include `Closes #987`.
- Merge is allowed only after Loom merge checkpoint and PR gate consume fresh or carrier-only review evidence.
