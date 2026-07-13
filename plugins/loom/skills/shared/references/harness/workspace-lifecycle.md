# Workspace Lifecycle

Each executable Work Item uses one issue-scoped branch and one formally
registered worktree. The authoritative binding comes from explicit CLI input,
Git, and GitHub readback.

## Create and check

```bash
loom workspace create --target <repo> --item <owner/repo/work_item/id> --branch <branch> --json
loom workspace check --target <worktree> --item <owner/repo/work_item/id> --json
```

Creation does not require a diff, commit, or PR. It must not read or write a
repository current pointer.

## Retire

```bash
loom workspace retire --target <worktree> --item <owner/repo/work_item/id> --json
```

Retirement is `local_only`. It may remove only the explicit, owned, clean
worktree after host completion is read back. It must not delete dirty or
unowned content, mutate GitHub, or write repository carriers. Failure leaves the
worktree intact and reports one precise remediation.
