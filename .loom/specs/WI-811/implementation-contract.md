# WI-811 Implementation Contract

## Allowed Change Surface

- `src/skills/shared/scripts/governance_surface.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/shared/references/adoption/github-profile-upgrade.md`
- `skills/shared/scripts/governance_surface.py`
- `skills/shared/scripts/loom_check.py`
- `skills/shared/references/adoption/github-profile-upgrade.md`
- Generated `skills/**/.loom-runtime/shared/scripts/governance_surface.py`
- Generated `skills/**/.loom-runtime/shared/scripts/loom_check.py`
- Generated `skills/**/.loom-runtime/shared/references/adoption/github-profile-upgrade.md`
- `docs/adoption/github-profile-upgrade.md`
- `docs/evidence/validations/validation-adoption-gate-rollout.md`
- Loom Work Item, progress, spec, review, status, and shadow carriers for `WI-811`

## Required Properties

- New adoption remains advisory by default.
- `target_mode` mirrors the recommended target mode and cannot become blocking unless every precondition passes.
- Passing blocking preconditions must declare version-controlled evidence locators.
- Rollback preserves evidence and only pauses blocking consumption by returning to advisory.
- Rollback drift coverage must include runtime, evidence, host binding, review head, and metadata parsing.

## Exit Criteria

- PR is bound to `WI-811` and #811.
- Local validation and GitHub PR checks pass.
- PR merges to `main`.
- #811 and Project #4 synchronize with PR/merge closeout evidence.
- #808 parent FR is updated after #811 closeout.
