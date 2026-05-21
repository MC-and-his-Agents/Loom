# WI-805 Spec

## Outcome

Loom reconciliation sync exposes a stable safe sync plan before any GitHub write, so agents can review closeout/project/comment writes as evidence-backed planned actions and keep dry-run as the default path.

## Acceptance

- `reconciliation sync` emits `loom-safe-sync-plan/v1`.
- Dry-run is the default behavior; GitHub writes require explicit `--apply`.
- Planned writes are limited to `close_issue`, `set_project_done`, and `add_closeout_comment`.
- Each planned write carries source finding, proof locator, write target, and rollback note.
- Block findings and missing proof do not produce host writes.
- `loom_check` validates safe sync fixtures and dry-run write guards.
- Generated skills/runtime surfaces stay synchronized with `src/skills`.

## Non Goals

- Do not add repo-specific closeout rules to Loom core.
- Do not introduce a second truth source for GitHub issue or Project state.
- Do not expand this Work Item into GitHub profile, Governance Lint, or complex-existing migration behavior.
