# WI-1738 Implementation Contract

## Implementation Scope

- `loom ship` infers missing branch, head SHA, and target branch from PR readback and current checkout state.
- Explicit CLI arguments remain authoritative when they agree with host readback.
- Explicit argument conflicts with PR readback fail closed before mutating gates.
- Delegated metadata, PR gate, controlled merge, and closeout branch selection consume effective inferred or explicit bindings.
- Short diagnostic output includes blocked/fixed/next-action compatible binding inference details, while full payload remains available through existing JSON/full-output surfaces.

## Non-Goals

- No release publish behavior changes.
- No review stale classifier changes.
- No validation profile selector changes.
- No automatic carrier/shadow repair chain changes beyond passing inferred metadata to existing delegated gates.

## Compatibility

Existing explicit `--branch`, `--head-sha`, and `--target-branch` usage remains supported. Existing `--pr-payload-file` fixture paths remain supported and are used for deterministic tests.
