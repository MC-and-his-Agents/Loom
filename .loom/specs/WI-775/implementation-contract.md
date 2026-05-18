# WI-775 Implementation Contract

## Source Truth

- Source edits live under `src/skills/**` and `docs/adoption/**`.
- Generated `skills/**`, `tools/**`, and `examples/new-project/.loom/**` are refreshed from source commands, not hand-maintained as independent truth.

## Behavior Boundaries

- `--intent` is an input signal and output fact, not a full profile system in this checkpoint.
- Unspecified intent may continue light-governance bootstrap for a new project.
- Unspecified intent must block writes when the recommended path is `full-bootstrap`.
- `attach-only` must avoid generated Loom work item, progress, and status truth in this checkpoint.
- Later issues own stronger profile, attach-only forbidden-carrier, gitignore, Git visibility, pre-execution, and decision-prompt behavior.

## Evidence Boundary

- Local validation must prove both negative and positive paths: read-only no planned writes, attach-only forbidden carriers absent, ambiguous full-bootstrap blocked, and explicit execution-control generated.
- Review conclusions must call out any behavior intentionally deferred to later adoption/install safety issues.
