# WI-968 Spec

## Acceptance

- Default local/CI checks must consume a lightweight loom_check runtime regression entrypoint.
- The regression must prove same-worktree double start fails fast with owner diagnostics without launching a second full check.
- Different worktree roots must resolve to distinct worktree-local lock paths.
- Default subprocess helpers must strip host/Codex App pollution while explicit fixture env injection remains possible.
- Missing live target samples must use unique absent temp paths, not a fixed `/tmp/loom-missing-live-target`.
- Node installer regression must report readable owner diagnostics when the package-root regression lock is busy.
- Demo bootstrap fixture checking must leave `examples/new-project` clean.

## Non-Goals

- Do not make the heavy full-check concurrency matrix mandatory in CI.
- Do not depend on live GitHub or a real Codex App socket.
- Do not expand into #969 review profile, #953 source self-check layering, #866 closeout gate, #873 PR metadata, or CLI-first mainline.
