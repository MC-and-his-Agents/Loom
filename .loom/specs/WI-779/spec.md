# WI-779 Spec

## Acceptance

- `small-existing` with `light-governance` keeps lightweight retrofit to repo companion, bootstrap metadata, review guidance, lightweight review placeholders, and PR template surfaces.
- `light-governance` does not generate, declare, or leave `.loom/work-items/**`, `.loom/progress/**`, `.loom/status/current.md`, or `.loom/specs/**`.
- `light-governance` dry-run/write output marks these execution-control carriers in `intentionally_absent` and defers them to explicit `execution-control`.
- `verify` fails closed when a `light-governance` target contains or declares those execution-control carriers.
- `execution-control` still generates and declares work item, progress, status, and formal spec carriers.
- Adoption docs and generated skill surfaces describe the same boundary as the runtime.

## Non-Goals

- Do not change release target truth defaults; that remains #780.
- Do not change blanket `.loom` gitignore handling; that remains #781.
- Do not change stable carrier Git visibility requirements; that remains #782.
