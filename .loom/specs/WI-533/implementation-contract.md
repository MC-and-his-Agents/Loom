# WI-533 Implementation Contract

## Write Scope

- `VERSION`
- generated `skills/**/loom-package.json` repo_version metadata
- `packages/loom-installer/package.json`
- `packages/loom-installer/package-lock.json`
- `.loom` `WI-533` work item, progress, specs, review, status, and bootstrap carrier bindings
- `docs/evidence/v0.10.0-release-readiness.md`

## External Actions

- Create the final closeout PR for the `v0.10.0` repository release.
- After merge and post-merge verification, create GitHub tag/release `v0.10.0`.

## Guardrails

- Do not change already merged v0.10.0 candidate implementation scope.
- Do not create the `v0.10.0` release before the closeout PR is merged to `main`.
- Do not claim repository release truth has advanced while `VERSION` and generated `repo_version` metadata still declare `v0.9.0`.
