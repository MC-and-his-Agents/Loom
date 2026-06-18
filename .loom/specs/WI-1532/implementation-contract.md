# WI-1532 Implementation Contract

- Suite path: minimal

## Contract Surface

- `loom gate freeze check --profile closeout` emits `loom-closeout-freeze/v1`.
- The payload contains terminal subject, host git, dependency graph, retained review, carrier refresh, shadow freshness, PR body readback, release boundary, and allowed-path bindings.
- `readiness.closeout_pr_allowed` is true only when all required closeout admission inputs pass.
- Carrier refresh, shadow freshness, readback drift, release/no-release evidence gaps, retained review drift, dependency drift, and disallowed path drift are blocking inputs.
- `consumed_contract_fields` records stabilized #1510/#1512/#1513 fields; only genuinely future fields remain in `pending_contract_fields`.
- The implementation is read-only and does not mutate GitHub or versioned carrier truth.

## Consumer Boundary

- #1533 may consume this as the local closeout admission input surface.
- #1534 may document the surface after #1533 stabilizes.
- #1515 may readback #1532 completion evidence but must still perform final release/no-release closeout.

## Non-Goals

- No hosted closeout-specific gate implementation.
- No closeout run orchestration.
- No release, tag, GitHub Release, npm publish, Project mutation, issue closure, PR creation, or carrier repair.

## Validation Binding

- Targeted closeout freeze fixture in `tools/check_cli_contract.py`.
- Source/shared/generated runtime parity.
- Suite evidence/carrier validation for WI-1532.
- Local fact-chain and shadow parity after carrier registration.
