# WI-1582 Plan

## Implementation Goal

Deliver the closeout hosted admission repair under a legal WI-1582 fact chain, branch, review, and PR carrier.

## Implementation Steps

1. Preserve `surface=closeout` in hosted freeze recomputation.
2. Make terminal closeout review/carrier freshness surface-aware only when the requested surface is `closeout` and the current checkpoint is terminal.
3. Expose `carrier refresh --surface closeout` and hosted `gate-freeze check --surface closeout`.
4. Keep merge-ready/current-head review paths strict.
5. Sync source, shared, generated runtime copies, and demo bootstrap fixtures.

## Validation

- S1 -> automated: targeted terminal closeout hosted fixture via `assert_terminal_closeout_pr_gate_fixture(Path(tmp))`.
- S2 -> automated: same fixture verifies closeout terminal pass and merge-ready regression block.
- S3 -> automated: same fixture checks `carrier refresh --surface closeout` and hosted `gate-freeze check --surface closeout`.
- A1 -> test evidence: targeted terminal closeout hosted fixture.
- A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`.
- A3 -> structural check: `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`.
- A4 -> test evidence: `make loom-demo-new-project-check`.
- A5 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`.

## Deferred Items

### Deferred Item 1

- Locator: #1554
- Reason: wrapper/runtime argument contract is broader than closeout admission.
- Activation condition: resume the wrapper contract lane.
- Does not currently block: WI-1582 implementation and validation.
- Statement: deferred is not completed.

### Deferred Item 2

- Locator: #1555
- Reason: one-shot post-merge closeout run depends on closeout queue/item binding product work.
- Activation condition: after #1494/#1543 inputs are stable.
- Does not currently block: WI-1582 implementation and validation.
- Statement: deferred is not completed.

## Boundaries

- Do not reopen or rewrite WI-1512 terminal closeout truth.
- Do not bind this Work Item to WI-1578.
- Do not mutate #1580 closeout-only carrier in this PR.
- Do not weaken merge-ready/current-head review semantics.

## Ready For Review

- Build checkpoint must pass.
- Suite validate, suite evidence validate, and suite carrier validate must pass.
- Authored review must bind to the current head and latest validation summary.
