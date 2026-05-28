# WI-1120 Implementation Contract

## Owned Surface

- `loom suite validate` core read-only command.
- CLI contract fixtures proving the core result envelope.

## Required Behavior

- The command must never mutate the target repository.
- Missing `--item` or unsafe item ids fail closed.
- Missing suite path decisions return `block` with `missing_suite_path_decision`.
- Missing required artifacts return `block` with `missing_required_artifact`.
- Valid minimal and complete full suite fixtures return `pass`.
- `not_applicable` path decisions return `not_applicable`.
- Deferred evidence, consistency, and carrier surfaces may be advisory in #1120.

## Forbidden Surface

- No GitHub issue, Project, PR, branch, worktree, or host-control mutation.
- No review record, merge-ready result, closeout result, runtime attempt, shadow truth, task carrier, or status truth mutation by the CLI command.
- No generated skills, plugin, workflow, or PR template mutation.
- No `/speckit.*` command names or `.specify/` layout.
