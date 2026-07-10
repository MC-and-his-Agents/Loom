# WI-1691 Implementation Contract

## Runtime Contract

- `loom ship --apply --item <id> --issue <n> --pr <n> --json` emits a `loom-ship/v1` apply payload.
- Apply payload includes safe metadata repair, PR metadata preflight, PR gate, controlled merge check, closeout policy, controlled merge apply, host reconciliation sync, and host closeout check steps.
- `mutates` is `true` for apply payloads because safe repair, controlled merge, and host reconciliation can write host state.

## Delegation Contract

- Apply mode preserves the same read-only gate sequence as dry-run before executing merge.
- Controlled merge execution delegates `controlled-merge merge --execute`; it must not pass `--apply` to the controlled-merge runtime.
- Host closeout delegates `reconciliation sync --apply` and `closeout check`.
- `ship --apply` must not call `carrier closeout-sync --apply` by default.

## Closeout Policy Contract

- `inline` and `host_only` policies are eligible for default ship apply.
- `batched_carrier_pr` and `full_closeout_pr` policies fail closed before merge and point to explicit closeout paths.
- `no_release` must not be interpreted as a release trigger.

## Boundary Contract

- #1691 does not add a controlled-merge `--closeout-run` flag; #1692 owns that surface.
- #1691 does not publish releases or rewrite README/skills guidance.
- #1691 does not make host state a second repository truth source; it consumes host readback through existing reconciliation and closeout gates.
