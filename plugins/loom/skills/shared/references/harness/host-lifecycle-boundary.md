# Host Lifecycle Boundary

The lifecycle binding is:

```text
typed Work Item -> issue-scoped branch -> formal worktree -> GitHub PR -> head SHA
```

`route`, `build`, `pre-review`, `review`, `merge-ready`, and `ship` derive this
binding from explicit input plus GitHub/Git readback. A PR is not required before
`build`; a real Work Item, branch, and formal worktree are sufficient.

Committed current/status/progress/review/shadow files are not lifecycle input.
Stale legacy files are diagnostics only and cannot block or redirect the public
path.

Before a host mutation, Loom verifies the typed subject, current PR head,
required checks, target branch, and relevant attestation. After the mutation it
reads the same host object back. Missing or partial readback fails closed with a
host-specific cause.

See [host-action-contract.md](./host-action-contract.md).
