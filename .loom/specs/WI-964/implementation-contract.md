# WI-964 Implementation Contract

## Write Scope

- `src/skills/shared/scripts/loom_check.py`
- Generated `skills/**/shared/scripts/loom_check.py` surfaces
- WI-964 Loom carriers and spec/review records

## Guardrails

- The lock path must be inside the target root.
- The default behavior is fail-fast, not unbounded waiting.
- Busy output must expose enough owner data for an operator to decide whether to wait, remove a stale lock, or use another worktree.
- Test fixtures must not leave `.loom/runtime/loom_check.lock`, `__pycache__`, or other runtime residue in the worktree.
