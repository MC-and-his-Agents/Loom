---
name: loom-build
description: Execute a bounded Work Item after host-native admission and before pre-review.
---

# Loom Build

Use for implementation of one bounded, typed Work Item in its formal
issue-scoped worktree.

```bash
loom build \
  --target <repo> \
  --item <owner/repo/work_item/id> \
  --issue <id> \
  --branch <issue-scoped-branch> \
  --json
```

Build is valid before a PR exists. It consumes the explicit GitHub Work Item,
branch, worktree, and repository-native validation entrypoints. It does not
require a diff, empty commit, empty PR, formal-suite carrier, current pointer,
status/progress file, review record, shadow, or closeout carrier.

Subagent output is evidence only after the primary agent integrates and
verifies it. Finish when the bounded implementation and targeted validation
are stable enough to create a real PR and run `loom pre-review`.
