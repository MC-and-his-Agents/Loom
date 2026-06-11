# WI-1243 Implementation Contract

## Contract Boundary

- `runtime_provider: global-cli` remains the active provider proof; retained `.loom/bin` is residue, not current runtime truth.
- Runtime-carrier migration must stay distinct from skills/plugin payload migration.
- Retained `.loom/bin` deletion must remain proposal-only until an explicit apply/confirmation contract exists.
- Repo-local gate carriers that still reference `.loom/bin` block deletion planning and must be reported exactly.

## Implementation Surfaces

- `tools/loom.py`: runtime-carrier migration action generation and blocker reporting in repair/upgrade planning.
- `tools/check_cli_contract.py`: eligible and blocked retained-`.loom/bin` fixture coverage.
- `docs/adoption/loom-installed-state-v2.md` and `docs/adoption/cli-first-legacy-migration-playbook.md`: adoption contract updates for runtime-carrier migration semantics.

## Non-Goals

- Mutating `loom repair apply`.
- Shared carrier-lane updates in `.loom/status/current.md` or `.loom/shadow/**`.
- #1244/#1245/#1246 follow-up batches.
