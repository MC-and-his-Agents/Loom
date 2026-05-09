# WI-532 Implementation Contract

## Write Scope

- `VERSION`
- generated `skills/**/loom-package.json` repo_version metadata
- `packages/loom-installer/package.json`
- `packages/loom-installer/package-lock.json`
- `.loom` WI-532 work item, progress, specs, review, status, and bootstrap carrier bindings

## External Actions

- Create the final closeout PR for #532.
- After merge and post-merge verification, create GitHub tag/release `v0.9.0`.
- Close #532 after release truth and issue truth agree.

## Guardrails

- Do not change completed FR implementation scope.
- Do not create the `v0.9.0` release before the closeout PR is merged to main.
- Do not close #532 before the release/tag exists at the verified final release commit.
