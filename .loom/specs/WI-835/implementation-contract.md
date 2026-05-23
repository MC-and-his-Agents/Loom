# WI-835 Implementation Contract

## Owned Paths

- `docs/adoption/complex-existing-authority-migration-playbook.md`
- `docs/evidence/fixtures/complex-existing-authority-migration-fixtures.json`
- `docs/adoption/README.md`
- `docs/adoption/deep-existing-repo-default.md`
- `docs/adoption/repo-interop-contract.md`
- `docs/methodology/harness/review-execution.md`
- `docs/methodology/harness/controlled-merge.md`
- `src/skills/**`
- `skills/**`
- `examples/new-project/.loom/**`
- `.loom/work-items/WI-835.md`
- `.loom/progress/WI-835.md`
- `.loom/reviews/WI-835*.json`
- `.loom/specs/WI-835/**`

## Required Validation

- `python3 tools/skills_surface.py check`
- `make py-compile`
- `python3 tools/loom_check.py`
- `make check`

## Merge Contract

- PR body must include `Closes #836` through `Closes #842`.
- PR body must bind `Loom Work Item: WI-835`.
- Parent #835 is closed only after PR merge, child closure, and Project reconciliation.
