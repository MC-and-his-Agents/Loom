---
name: loom-pre-review
description: Bind a real PR, current head, Work Item, branch, and formal worktree before semantic review.
---

# Loom Pre Review

Run after a real implementation PR exists:

```bash
loom pre-review \
  --target <repo> \
  --item <owner/repo/work_item/id> \
  --issue <id> \
  --pr <pr> \
  --branch <branch> \
  --json
```

The check reads GitHub and the formal worktree only. It verifies the PR is
open and ready, the closing Work Item is unique, branch and current head match,
and targeted validation input is stable. It does not produce a semantic review
verdict.

Do not run removed suite, gate-freeze, fact-chain, checkpoint, current, or
carrier commands. A failure returns one primary cause and one remediation.
Pass means the current head may enter `loom-review`.
