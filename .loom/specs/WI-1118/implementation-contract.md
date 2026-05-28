# WI-1118 Implementation Contract

## Owned Surface

- Contract-test coverage proving `loom suite scaffold` only writes the suite scaffold artifacts it owns.

## Required Behavior

- Dry-run remains read-only.
- Minimal apply creates only missing `spec.md` and `plan.md`.
- Full apply creates only missing `suite-index.md`, `spec.md`, `plan.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`.
- Existing forbidden truth surfaces are not modified.
- Scaffold JSON does not expose host/review/merge-ready/closeout/generated-skill action keys.

## Forbidden Surface

- No GitHub issue, Project, PR, branch, worktree, or host-control mutation.
- No review record, merge-ready result, closeout result, runtime attempt, shadow truth, task carrier, or status truth mutation.
- No generated skills, plugin, workflow, or PR template mutation.
- No `/speckit.*` command names or `.specify/` layout.
