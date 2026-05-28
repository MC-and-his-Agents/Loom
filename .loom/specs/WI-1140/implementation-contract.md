# WI-1140 Implementation Contract

## Consumed Contracts

- `docs/methodology/harness/full-spec-suite-cli-surface.md`
- `docs/methodology/templates/spec-suite.md`
- `docs/methodology/templates/evidence-map.md`
- `docs/methodology/harness/task-carrier-contract.md`
- `docs/methodology/harness/gate-chain.md`
- `src/skills/route-matrix.md`

## Required Behavior

- Scenario skill runtime must consume suite readiness from `loom suite ... --json`.
- `loom build` must expose `suite_validation` from `suite validate` and `suite_carrier_validation` from `suite carrier validate`.
- `loom spec-review` must consume `suite validate` before spec review approval.
- `loom pre-review`, implementation `loom review`, and `loom merge-ready` must continue consuming `suite evidence validate` and `suite carrier validate` as gate input evidence.
- Missing or unreadable suite CLI JSON must fail closed when suite readiness is required.
- Generated `skills/` and `.loom/bin/loom_flow.py` must stay synchronized with source runtime changes.

## Forbidden Behavior

- No embedded reimplementation of suite readiness rules in scenario skill runtime.
- No CLI output replacing Work Item, review record, merge-ready result, closeout evidence, docs/source truth, or Project truth.
- No host writes or reconciliation side effects.
- No consistency analyze implementation.
- No new issue-tree scope.
- No `/speckit.*` command names or `.specify/` layout.
