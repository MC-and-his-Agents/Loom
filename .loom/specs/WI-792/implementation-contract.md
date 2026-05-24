# WI-792 Implementation Contract

## Owned Surfaces

- `src/skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_check.py`
- `docs/evidence/phase-792-github-host-control-closeout.md`
- `docs/evidence/fixtures/safe-sync-plan-fixtures.json`
- Harness methodology and mirrored skill reference docs for native dependency and `loom_check` runtime behavior.
- Demo installed runtime fixture files required to keep source and consumer checks aligned.
- Loom carriers for PR #991 binding and stale WI-968 terminal cleanup.
- `packages/loom-installer/package.json` and `packages/loom-installer/package-lock.json` version metadata.

## Constraints

- GitHub state writes remain outside implementation until PR #991 is merged and closeout reconciliation is explicitly performed.
- Native dependency writes are dry-run only.
- Missing native dependency edges are not repo-authored truth.
- No destructive Git operation is allowed.
- Cleanup must remove only this run's temporary `loom-check-*` directories or lock files and must verify no `loom_check` subprocess remains.

## Review Basis

The authored review must bind to the PR #991 head and consume the validation summary from `.loom/progress/WI-792.md`.
