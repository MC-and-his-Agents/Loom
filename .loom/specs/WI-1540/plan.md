# WI-1540 Plan

## Implementation Steps

1. Keep WI-1538 terminal progress facts as `closed_out` after PR #1537 merge and issue #1538 closure readback.
2. Activate WI-1540 as the closeout-sync Work Item so PR #1539 consumes a fresh WI-1540 review instead of requiring a review on the terminal WI-1538 checkpoint.
3. Refresh active status and shadow hashes.
4. Validate fact-chain, shadow parity, PR metadata readback/preflight, current-head review, and local PR gate.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py pr-metadata preflight --target . --surface merge_ready --pr 1539 --head-sha 0ce75ba6ea0c88bb6974b1b645cbbfc8300b8aa5 --branch work/1538-closeout-sync --body-file .loom/tmp/pr-1539-rendered.md --compare-body-file .loom/tmp/pr-1539-readback.md`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py pr-gate check --target . --head-sha 0ce75ba6ea0c88bb6974b1b645cbbfc8300b8aa5 --branch work/1538-closeout-sync --pr 1539`
- `git diff --check`

## Dependencies

- Consumes closed #1538 and merged PR #1537.
- Unblocks #1529 review/purity and later milestone/12 work that shares the root workspace.

## Scope Guard

- Do not change runtime, hosted gate, PR gate, closeout profile, downstream implementation, release mechanics, or external host settings.
- Do not rewrite WI-1538 or WI-1531 retained review history.
