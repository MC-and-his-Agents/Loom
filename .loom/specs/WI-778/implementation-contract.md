# WI-778 Implementation Contract

## Source Truth

- Source edits live under `src/skills/**`, `Makefile`, and root Loom carriers for WI-778.
- Generated `skills/**` and `examples/new-project/.loom/**` are refreshed from source commands, not edited as independent truth.

## Behavior Boundaries

- Scaffold profile selection is the stable mapping from adoption intent to write surface.
- `light-governance` must not author Loom-owned work item, progress, or status carriers.
- `execution-control` and `strong-governance` may continue sharing the same concrete write files in this checkpoint, but must remain distinguishable profiles in output.
- Release placeholder, `.gitignore`, Git visibility, attach-only semantic hardening, pre-execution classification, and decision prompts remain deferred to their ordered issues.

## Evidence Boundary

- Validation must compare dry-run planned paths with fresh write touched paths for representative profiles.
- Review conclusions must call out the intentionally deferred policy changes so later checkpoint scope remains clear.
