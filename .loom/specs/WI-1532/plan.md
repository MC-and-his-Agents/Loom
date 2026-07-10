# WI-1532 Plan

## Implementation Steps

1. Extend the gate freeze runtime to support a closeout profile and emit `loom-closeout-freeze/v1` payloads.
2. Read terminal subject inputs: issue, implementation PR, merge commit, target branch, Work Item, and target branch containment.
3. Consume dependency graph, retained review, PR body readback, carrier refresh, shadow freshness, release/no-release evidence, and closeout-only allowed paths.
4. Convert each failed input into stable failure kinds, next actions, and `closeout_pr_allowed=false`.
5. Record consumed stable contract fields and avoid leaving #1510/#1512/#1513 fields marked pending.
6. Add targeted fixture coverage for pass, release evidence gap, PR body drift, carrier/shadow stale, dependency drift, allowed path drift, and retained review drift.
7. Sync source, shared, and generated skill runtime copies.

## Validation

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py`
- `/usr/bin/cmp src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py`
- `/usr/bin/cmp` for every `skills/loom-*/.loom-runtime/shared/scripts/loom_flow.py`
- Targeted `assert_closeout_freeze_profile_fixture`
- `python3 tools/loom.py gate freeze check --target . --profile closeout --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1532 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1532 --json`
- `python3 .loom/bin/loom_init.py fact-chain --target .`
- `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`

## Dependencies

- Hard dependency: #1531 closeout terminal profile contract.
- Consumes #1510 carrier/shadow freshness, #1512 hosted freeze input shape, #1513 classifier vocabulary, #1541 PR metadata readback, and #1543 closeout queue/status as stable upstream surfaces.
- Downstream: #1533 consumes the closeout freeze admission output; #1534/#1515 consume #1532 only after merge and closeout evidence.

## Scope Guard

- No host writes.
- No one-shot closeout run.
- No final release/no-release closeout.
- No docs/skills convergence outside minimum suite carriers for this Work Item.
