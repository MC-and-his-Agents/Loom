# WI-811 Spec

## Outcome

GitHub profile upgrade output exposes a machine-readable gate rollout contract that keeps new and incomplete repositories in advisory mode while preserving a controlled path for future blocking adoption and rollback.

## Acceptance

- `gate_rollout` includes `default_mode`, `current_mode`, `recommended_mode`, `target_mode`, `blocking_allowed`, `blocking_preconditions`, and `rollback`.
- Default, current, recommended, and target mode remain `advisory` unless every blocking precondition is passing with version-controlled evidence.
- Blocking preconditions identify strong maturity, adversarial adoption checks, and rollback switch, including evidence locator and version-controlled status.
- Rollback switches back to advisory and structures drift conditions for runtime, evidence, host binding, review head, and metadata parsing drift.
- `loom_check` rejects missing target mode, unsafe blocking recommendation, missing precondition evidence, and incomplete rollback drift coverage.
- Documentation and shared skill references describe the same rollout and rollback contract.

## Non Goals

- Do not modify GitHub branch protection or required checks.
- Do not enable blocking gates.
- Do not create repo-specific rules or host-private implementations in Loom core.
- Do not change review engine authority contracts owned by the complex-existing line.
