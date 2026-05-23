# WI-964 Spec

## Acceptance

- `loom_check` creates a same-worktree single-flight lock before source or consumer checks enter their heavy validation path.
- The lock is scoped under the checked worktree, not under a machine-global or cross-repository path.
- The lock owner payload includes `run_id`, `pid`, `started_at`, `command`, and `cwd`.
- A second run in the same worktree fails fast with readable owner and fallback output.
- Stale locks from dead owners can be recovered by a later run.
- Different worktrees are not blocked by this lock.

## Non-Goals

- Do not serialize all Loom subcommands.
- Do not implement #967 host environment cleanup, #965 fixture isolation, #966 installer write isolation, or #968 regression matrix.
