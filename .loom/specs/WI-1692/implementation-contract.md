# WI-1692 Implementation Contract

## Runtime Contract

- `loom merge run <pr> --apply` remains a compatibility-preserving wrapper over `controlled-merge merge --execute`.
- `loom merge run <pr> --apply --closeout-run` is explicit opt-in behavior and emits a `loom-merge-run/v1` payload.
- `--closeout-run` requires `--work-item`, `--issue`, and a target branch from `--target-branch` or PR base readback.

## Closeout Policy Contract

- `--closeout-mode inline` runs existing closeout-run after controlled merge passes.
- `--closeout-mode host_only` runs host reconciliation and closeout readback after controlled merge passes, without carrier closeout-run.
- `--closeout-mode batched_carrier_pr` and `--closeout-mode full_closeout_pr` fail closed before controlled merge.
- The command reports `creates_closeout_pr=false`; it never creates a closeout PR.

## Failure Contract

- If controlled merge blocks, closeout-run is not started.
- If closeout target branch cannot be inferred, the command blocks after reporting the missing closeout input.
- If upgraded closeout modes are requested, the command blocks before merge and points to explicit queue or full closeout paths.

## Boundary Contract

- This Work Item does not replace `loom ship` as the user-facing delivery entry.
- This Work Item does not change runtime `loom_flow.py` controlled-merge internals.
- This Work Item does not document or market the path; #1694 owns README, skills, and fixtures convergence.
