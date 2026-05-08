# WI-689 Implementation Contract

## Write Scope

- `.loom/work-items/WI-689.md`
- `.loom/progress/WI-689.md`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/specs/WI-689/`
- `docs/adoption/`
- `packages/loom-installer/`

## Constraints

- `upgrade-plan` and `verify-upgrade` must be read-only for the target repository.
- Installer status metadata is evidence about the installed layer only; it cannot become Work Item, PR, review, or closeout truth.
- Unknown, missing, or inconsistent metadata must fail closed with a visible failed layer and reason.
- Failed rehearsal evidence must include a rollback path when an installed layer path is known.
