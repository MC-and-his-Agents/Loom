# WI-1690 Implementation Contract

## Runtime Contract

- `loom ship --item <id> --pr <n> --intensity auto --json` emits a `loom-ship/v1` dry-run payload.
- The dry-run payload includes PR metadata preflight, PR gate, controlled merge check, closeout policy, skipped post-merge closeout, first blocker, and next action.
- `mutates` is `false` for #1690.

## Delegation Contract

- Dry-run delegates only read-only runtime checks.
- Delegated arguments must not include `--apply`, `--execute`, or any host-write flag.
- The dry-run uses existing root wrapper delegation and must not introduce a separate orchestration engine.

## Closeout Policy Contract

- Light-intensity work without release or versioned carrier triggers selects host-only closeout and does not create a closeout PR by default.
- Reinforced, release, version, parent, milestone, multi-item, security, permission, or conflict signals upgrade to an explicit closeout path.
- `no_release` must not be interpreted as a release trigger.

## Boundary Contract

- `loom ship --apply` fails closed in #1690 and points to #1691.
- This Work Item does not merge PRs, close issues, publish releases, write GitHub, or write repo carriers from `loom ship`.
