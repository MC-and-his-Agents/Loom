---
name: loom-resume
description: Rebuild execution context from explicit host and worktree facts without a repository current pointer.
---

# Loom Resume

Resume is a scenario, not a CLI command. Require the explicit Work Item and
formal issue-scoped worktree, then derive context with:

```bash
loom status --target <repo> --json
loom workspace check --target <repo> --item <typed-work-item> --branch <branch> --json
```

If the subject is still an FR or Phase, use `loom route` to plan or select a
native Work Item before implementation. If a PR exists, read it from GitHub and
bind its branch/head; if no PR exists, continue through `loom-build` without
creating an empty commit or PR.

Never read or repair repo current, progress, review, shadow, or closeout
carriers. Resume is complete when Work Item → branch → formal worktree → PR
(when applicable) → current head is consistent and the next public command is
known.
