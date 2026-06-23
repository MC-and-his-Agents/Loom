# WI-1776 Implementation Contract

## Scope

- Runtime owner: `tools/loom.py`.
- Contract regression owner: `tools/check_cli_contract.py`.
- Fixture owner: `docs/evidence/fixtures/release-readback-fixtures.json`.
- Loom carriers: `.loom/work-items/WI-1776.md`, `.loom/progress/WI-1776.md`, `.loom/status/current.md`, `.loom/reviews/WI-1776*.json`, and `.loom/specs/WI-1776/*`.

## Required Behavior

- `loom release readback` remains read-only and must not publish, tag, create a GitHub Release, trigger workflow_dispatch, mutate npm, or write carriers.
- `loom release resume` remains read-only and exposes a resume contract over the same verdict payload.
- Release-required verdicts are limited to `published`, `missing`, `drifted`, and `blocked`.
- `published` requires tag, GitHub Release, npm package, successful target workflow, passing package surface, and terminal carrier state.
- `missing` covers absent release artifacts without overwriting existing tag, GitHub Release, or npm package.
- `drifted` covers release evidence bound to the wrong target commit or dist-tag.
- `blocked` covers readback errors, failed workflow, package surface mismatch, published artifacts with active carrier, and same-head main-worktree-busy fallback.
- Default diagnostics expose `verdict`, `blocked`, `gaps`, and `next_action`.

## Non-Goals

- No version bump for v0.21.0.
- No tag, GitHub Release, npm publish, or workflow dispatch.
- No destructive cleanup of worktrees or branches.
- No automatic host-safe worktree locator generation.
- No new release framework or CI workflow design.
