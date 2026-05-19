# WI-777 Spec

## Intent

When static repository signals support more than one reasonable adoption path, `loom-init bootstrap` must expose that choice as a structured decision prompt instead of presenting the heuristic recommendation as the only answer.

## Acceptance Criteria

- Dry-run bootstrap output includes a `decision_prompt` when repository signals and adoption intent diverge or when multiple adoption intents remain reasonable.
- The prompt names the repository shape, candidate intents, recommended default, risk differences, planned write targets, and verification entries.
- `--write` fails closed when intent is missing or inferred and the selected path would author heavy execution-control carriers.
- Explicit `--intent execution-control` still permits the heavy path after the operator makes that intent explicit.
- Prompt evidence can be consumed later as adoption decision source locator, reasoning, writeback target, and verification evidence.

## Non-Goals

- Do not promote repo-specific guardian, Project, release, or review rules into Loom core defaults.
- Do not change attach-only ownership rules from #784.
- Do not replace adoption intent with automatic repository classification.
