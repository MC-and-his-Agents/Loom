# WI-1109 Spec

## Goal

Implement the first read-only `loom suite inspect` JSON surface.

## Scope

- Add root CLI routing for `loom suite inspect --target <repo> --item <item> --json`.
- Return the standard `loom-cli-output/v1` envelope.
- Preserve `mutates: false`.
- Return `payload.suite_path: unknown` when no suite path decision can be derived.
- Include an inspect-only missing input for `suite_path_decision`.

## Boundaries

- Do not write repository files or host state from `suite inspect`.
- Do not implement readiness validation, artifact inventory derivation, scaffold generation, gate integration, merge-ready truth, closeout truth, or spec-kit command names/layout.

## Scenarios

### S-1109-1 Unknown Suite State

Given a target repository with no readable suite path decision,
When `loom suite inspect --target <repo> --item WI-1109 --json` runs,
Then it emits a passing read-only JSON payload with `suite_path` set to `unknown`.

### S-1109-2 No Mutation

Given an empty target repository directory,
When `loom suite inspect` runs against that target,
Then the command leaves the target directory unchanged.

## Acceptance

- AC-1109-1: `suite inspect` emits `schema_version`, `command`, `result`, `target`, `item_id`, `summary`, `mutates`, and `payload`.
- AC-1109-2: unknown state is represented as `payload.suite_path: unknown`, not guessed.
- AC-1109-3: the focused CLI contract fixture proves the command is read-only.
