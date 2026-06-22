# WI-1737 Implementation Contract

## Implementation Scope

- Checkpoint writes must persist canonical enum values.
- Legacy or alias checkpoint values remain accepted on read.
- Fixture updates are limited to canonical checkpoint output.

## Non-Goals

- No new checkpoint states.
- No ship repair-chain behavior.
- No closeout policy changes.

## Compatibility

Consumers that read older checkpoint spellings continue to work through normalization before writes occur.
