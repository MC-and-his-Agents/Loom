# Subagent-Driven Execution

Subagent-driven execution is a bounded build mode inside the main Loom execution lane. It is not a worker daemon, queue lifecycle, review result, or second truth source.

Delegated goal semantics are defined in [../governance/goal-schema.md](../governance/goal-schema.md). This file only adds the execution ownership and integration boundary for subagent-driven work.

## Ownership Contract

Each delegated unit must declare:

- `parent_goal`
- `task_goal`
- `context_locators`
- `read_scope`
- `write_ownership`
- `non_goals`
- `validation_expectation`
- `output_format`
- `integration_target`

Delegation is allowed only when the task is bounded, context locators are precise, write ownership does not overlap another active delegation, and the main executor can integrate the result before review. If ownership overlaps, the build must fail closed or stay local.

The delegated goal is not a new `Work Item`. It must derive from the active `Work Item goal` or main `/goal`, and its completion claim remains local evidence until the main executor integrates and verifies it.

## Integration Boundary

Subagent output remains evidence until the main executor integrates it into existing Loom carriers:

- implementation files
- validation evidence
- recovery and status carriers
- later review inputs

Unintegrated session output is a build/readiness blocker. It must not be cited as completed Work Item truth, review truth, merge-ready truth, or closeout truth.

## Repeated Blockers

When multiple delegated units or repeated rounds report the same scope, design, or validation gap, Loom emits a repeated blocker signal. The required response is root-cause escalation in the main execution lane, not silent retry loops.

## `loom-build`

`loom-build` sits between `loom-resume` and `loom-pre-review`. Its read surface reports required build inputs, delegation evidence, integration evidence, ownership conflicts, repeated blocker signals, and whether the build can proceed toward review.
