# WI-1122 Implementation Contract

## Owned Surface

- `loom suite validate` not_applicable rationale and deferred distinction.
- CLI contract fixtures proving the #1122 result envelope.

## Required Behavior

- The command must never mutate the target repository.
- Minimal path readiness must not pass without valid not_applicable coverage for full-path artifacts.
- Suite-level not_applicable must not return `not_applicable` without valid suite-level rationale.
- A valid not_applicable record must include artifact binding, rationale, consumer boundary, and recheck condition.
- Deferred records must be reported separately and must not satisfy not_applicable readiness.
- Existing #1120/#1121 path, artifact, advisory, and read-only envelopes remain stable.

## Forbidden Surface

- No GitHub issue, Project, PR, branch, worktree, or host-control mutation.
- No review record, merge-ready result, closeout result, runtime attempt, shadow truth, task carrier, or status truth mutation by the CLI command.
- No generated skills, plugin, workflow, or PR template mutation.
- No `/speckit.*` command names or `.specify/` layout.
