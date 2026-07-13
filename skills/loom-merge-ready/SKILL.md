---
name: loom-merge-ready
description: Confirm current-head host attestation, hosted delivery gate, required checks, and mergeability.
---

# Loom Merge Ready

Use `loom merge-ready` for explicit preflight or `loom merge check` as the
controlled-merge read path. All inputs must identify the same PR/current head
and typed Work Item.

Merge-ready consumes:

- the authenticated current-head review artifact;
- the hosted `loom-delivery-gate` result for that head;
- GitHub required/triggered checks and mergeability;
- the formal branch/worktree binding.

It performs zero mutations and does not read or write repo review, current,
status, progress, shadow, freeze, or closeout carriers. Reinforced governance
only strengthens host review/validation. Removed carrier backends cannot be
enabled.

Pass allows `loom ship` or `loom merge run --apply`; it never replaces the host
merge action.
