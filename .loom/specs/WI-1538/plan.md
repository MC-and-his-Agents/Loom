# WI-1538 Plan

## Implementation Steps

1. Terminalize WI-1531 dynamic checkpoint, current stop, and next step while preserving its retained validation summary.
2. Activate WI-1538 as the carrier-only repair Work Item so PR gate consumes a fresh WI-1538 review instead of replacing WI-1531 implementation review.
3. Refresh active status and shadow hashes.
4. Validate fact-chain, shadow parity, review-history scope proof, and PR metadata readback.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
- `git diff -- .loom/progress/WI-1531.md .loom/reviews/WI-1531.json`
- `git diff --check`

## Dependencies

- Consumes closed WI-1531 and merged PRs #1535/#1536.
- Unblocks #1529 review/purity and later milestone/12 work that shares the root workspace.

## Scope Guard

- Do not change runtime, hosted gate, PR gate, closeout profile, downstream implementation, release mechanics, or external host settings.
- Do not rewrite WI-1531 implementation review history or retained validation summary.
