# WI-966 Spec

## Acceptance

- Node installer regression must run `npm ci`, `npm test`, and `npm pack --dry-run` through a single worktree-local installer regression lock.
- The lock owner diagnostics must include `run_id`, `pid`, `started_at`, `command`, and `cwd`, with a readable timeout fallback.
- The regression must use a unique npm cache for each run.
- `loom_check` must not run installer package build/test/pack paths outside the same lock when those paths read or write `node_modules`, `dist`, or `payload`.
- Payload drift checking must still rebuild payload deterministically and detect real drift.
- CI Node installer PR/release workflows must consume the locked regression entrypoint.

## Non-Goals

- Do not remove Node installer regression coverage.
- Do not require all worktrees to share `node_modules` or npm cache.
- Do not implement #968's broader regression matrix.
- Do not change #965 demo bootstrap fixture behavior, #969 review profile, #953 source self-check layering, or CLI-first mainline behavior.
