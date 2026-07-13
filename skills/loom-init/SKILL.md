---
name: loom-init
description: Loom root entry for detection, diagnosis, metadata-only adoption, and scenario routing.
---

# Loom Init

Use this root scenario to detect the repository state and choose one bounded
next scenario. It does not create execution carriers or guess a current item.

## Public path

1. Run `loom detect --target <repo> --json`.
2. Run `loom doctor --target <repo> --json` when installation or provider
   readiness is uncertain.
3. For an unadopted repository, route to `loom-adopt`.
4. For existing work, require an explicit Work Item/issue and route through
   `loom status`, `loom workspace check`, or `loom route`.

Repository adoption is metadata-only. Reinforced governance may strengthen
host review and validation, but never restores repo work-item, progress,
current, review, spec, shadow, or closeout carriers.

Finish when the next scenario, typed subject, formal worktree, and validation
boundary are explicit. See [../route-matrix.md](../route-matrix.md).
