# WI-1121 Implementation Contract

## Owned Surface

- `loom suite validate` path decision and required/conditional artifact validation.
- CLI contract fixtures proving the #1121 result envelope.

## Required Behavior

- The command must never mutate the target repository.
- Missing, invalid, or conflicting suite path decisions fail closed.
- Required artifacts must be present as ordinary files.
- Full path required artifacts are `suite-index.md`, `spec.md`, and `plan.md`.
- Minimal path required artifacts are `spec.md` and `plan.md`.
- Full path conditional artifacts are inventoried as conditional when absent.
- Existing #1120 pass, block, advisory, and not_applicable envelopes remain stable.

## Forbidden Surface

- No GitHub issue, Project, PR, branch, worktree, or host-control mutation.
- No review record, merge-ready result, closeout result, runtime attempt, shadow truth, task carrier, or status truth mutation by the CLI command.
- No generated skills, plugin, workflow, or PR template mutation.
- No `/speckit.*` command names or `.specify/` layout.
