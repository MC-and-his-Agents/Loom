# Workstation State Contract

Workstation state is private, derived, and non-authoritative. It may cache
repository discovery or plugin diagnostics, but it must never become repository
truth or a merge gate input.

## Current contract

- There is no public `loom workstation current` pointer.
- Commands receive a typed Work Item and derive branch, worktree, PR, and head
  from explicit input plus host readback.
- Codex owns marketplace registration, plugin cache, enablement, and task reload.
- Loom may report provider gaps through `loom doctor`; remediation is a typed
  Codex provider action, not a hidden CLI mutation.
- Local cache loss must not damage repository or GitHub truth.

Useful public readback:

```bash
loom workspace check --target . --item <owner/repo/work_item/id> --json
loom installed-state validate --target . --json
loom verify --target . --json
loom doctor --target . --json
```

Historical workstation registry schemas are compatibility input only. Removed
registration/current commands fail closed and do not recreate their state.
