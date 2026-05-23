# WI-963 Plan

## Implementation Steps

1. Add `docs/methodology/harness/loom-check-runtime-purity.md` as the unique contract landing point.
2. Add the shared reference under `src/skills/shared/references/harness/` and regenerate the checked-in `skills/` surface.
3. Link the contract from the harness README.
4. Extend `loom_check` source self-check with contract anchor validation.
5. Advance installer version metadata when the generated runtime distribution surface changes.
6. Validate with diff hygiene, Python compile, skills surface check, installer version bump check, source profile `loom_check`, git status, PR checks, and host-binding consistency.

## Boundaries

- Do not implement locking, temp path replacement, demo fixture isolation, Node installer isolation, or new concurrency tests in WI-963.
- Do not change installer regression behavior beyond the version metadata required by distribution gate.
- Do not alter closeout gate, PR metadata, review profile, #953 source self-check layering, or CLI-first behavior.
