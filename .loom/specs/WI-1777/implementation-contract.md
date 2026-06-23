# WI-1777 Implementation Contract

## Scope

- Runtime owner: `tools/loom.py`.
- Contract regression owner: `tools/check_cli_contract.py`.
- Loom carriers: `.loom/work-items/WI-1777.md`, `.loom/progress/WI-1777.md`, `.loom/status/current.md`, `.loom/reviews/WI-1777.json`, and `.loom/specs/WI-1777/*`.

## Required Behavior

- `loom ship status` and `loom ship preflight` are read-only command surfaces.
- Both commands read host issue/milestone state, target tag/GitHub Release/npm package presence, checkout freshness, and `.loom/status/current.md` carrier state.
- Default diagnostics expose a short blocked/fixed/next_action path.
- Full host/release/checkout/carrier payloads are only required under JSON/full-output consumption.
- Missing target release artifacts are valid absence signals; transport or malformed readback errors must surface as readback errors.
- A normal issue branch that is ahead of `origin/main` must not be reported as stale.

## Non-Goals

- No mutating closeout sync.
- No release readback verdict taxonomy.
- No publishing, tagging, or GitHub Release creation.
- No PR metadata race handling.
- No multi-worktree merge fallback automation.
