# WI-1124 Implementation Contract

## Ownership

- `tools/loom.py`: suite validate failure taxonomy metadata and payload projection.
- `tools/check_cli_contract.py`: fixtures that lock taxonomy fields for blocking and advisory suite validation findings.
- `docs/methodology/harness/full-spec-suite-cli-surface.md`: command surface status and finding field contract.
- `docs/methodology/harness/cli-command-matrix.md`: suite validate implemented scope.

## Non-goals

- Do not wire suite validate into `loom flow spec-review`; #1125 owns that.
- Do not add CLI writes, host writes, review writes, merge-ready writes, or closeout writes.
- Do not introduce `/speckit.*` commands or `.specify/` layout.
