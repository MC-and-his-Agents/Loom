# Validation: loom_check Runtime Regression Coverage

## Scope

This validation records #968 P0-A coverage for loom_check concurrency isolation and runtime-site purity.

Default local/CI entry:

```sh
make loom-check-runtime-regression
```

The target is also consumed by:

```sh
make loom-check
```

## Covered

- same-worktree `loom_check` double start fails fast with readable lock owner evidence
- different worktree roots use different worktree-local lock paths
- default subprocess helpers strip host/Codex App pollution while explicit fixture env injection remains possible
- missing live target samples use unique absent temp paths instead of fixed `/tmp/loom-missing-live-target`
- Node installer regression reports readable owner diagnostics when the package-root regression lock is busy
- demo bootstrap fixture check runs against an isolated copy and leaves `examples/new-project` clean

## Boundary

This is the default lightweight regression set. Heavy full-check concurrency matrices remain explicit opt-in validation and are not required on every CI run.
