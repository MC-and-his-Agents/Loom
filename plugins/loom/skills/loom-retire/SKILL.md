---
name: loom-retire
description: Retire a completed local issue-scoped worktree without changing host or repository truth.
---

# Loom Retire

After merge and host closeout readback, inspect the local cleanup plan:

```bash
loom workspace retire --target <repo> --item <typed-work-item> --json
```

Retirement is local-only. It does not close issues or PRs and does not write
progress, current, review, shadow, or closeout carriers. Preserve user changes;
remove the worktree/branch only through the repository's normal Git workflow
after confirming no uncommitted or unpushed work remains.

Finish when the local worksite is clean or has one explicit retention reason.
