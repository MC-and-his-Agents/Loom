# WI-778 Spec

## Goal

Define stable scaffold profiles for adoption intents so Loom bootstrap dry-run, write, and verify describe the same adoption surface.

## Acceptance Criteria

- Bootstrap output includes a top-level `scaffold_profile` with name, write behavior, work-item carrier behavior, and description.
- `observe-only` and `skill-install-only` remain non-writing profiles.
- `attach-only` writes companion/read surfaces without review/spec/work/progress/status execution carriers.
- `light-governance` writes companion, review/spec, and PR-template surfaces without Loom-owned work item, progress, or status carriers.
- `execution-control` writes Loom-owned work item, progress, review, status, and spec carriers.
- `strong-governance` has its own profile while preserving the current execution-control write surface for this checkpoint.
- `initial_artifacts`, `planned_writes`, actual write behavior, and verify required paths are profile-aligned.
- Bootstrap output includes top-level `upgrade_triggers` derived from deferred capabilities and the active profile.
- Generated skills surfaces and `examples/new-project` are refreshed from source.

## Non-goals

- Do not harden attach-only forbidden carrier scanning; #784 owns that.
- Do not remove placeholder release target truth; #780 owns that.
- Do not change blanket `.loom` gitignore behavior or Git visibility checks; #781 and #782 own those.
- Do not add pre-execution existing classification or decision prompts; #776 and #777 own those.
