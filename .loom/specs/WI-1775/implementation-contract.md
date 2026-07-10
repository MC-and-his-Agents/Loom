# WI-1775 Implementation Contract

## Scope

- Runtime owner: `tools/loom.py`.
- Contract regression owner: `tools/check_cli_contract.py`.
- Loom carriers: `.loom/work-items/WI-1775.md`, `.loom/progress/WI-1775.md`, `.loom/status/current.md`, `.loom/reviews/WI-1775.json`, and `.loom/specs/WI-1775/*`.

## Required Behavior

- `loom closeout status` is read-only and reports PR metadata readback, host closeout readiness, and terminal cleanup state.
- `loom closeout sync` defaults to dry-run and reports the repair plan without claiming fixed state.
- `loom closeout sync --apply` may apply PR metadata repair and existing closeout reconciliation/carrier refresh flow before final readback.
- PR metadata readback must run before closeout run consumption unless explicitly skipped.
- If PR metadata readback blocks and `--apply` is set, metadata update must apply and then readback again before closeout run is consumed.
- Terminal cleanup check is read-only; it reports cleanup-needed actions for issue worktree, local branch, and remote branch, and blocks on dirty/unreadable main worktree state.
- Default diagnostics expose blocked/fixed/next_action and cleanup verdict.

## Non-Goals

- No release verdict taxonomy.
- No tag, GitHub Release, or npm publish readback.
- No publishing, tagging, or GitHub Release creation.
- No automatic branch or worktree deletion.
- No multi-worktree merge fallback automation.
