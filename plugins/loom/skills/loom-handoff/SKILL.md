---
name: loom-handoff
description: Prepare a session handoff from public derived state without repository mutations.
---

# Loom Handoff

Handoff is a conversation artifact, not a CLI command or repository carrier.
Read `loom status` and `loom workspace check`, then summarize:

- objective and bounded scope;
- typed Work Item, branch, formal worktree, PR, and current head;
- completed changes and targeted validation;
- current-head review/gate locators when they exist;
- one next action and any real blocker.

Do not write current, recovery, progress, review, shadow, or closeout files.
The receiving agent must read back live GitHub/worktree facts before continuing.
