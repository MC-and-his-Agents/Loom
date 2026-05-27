# WI-1118 Spec

## Goal

Prove `loom suite scaffold` remains a repo-local scaffold writer and cannot mutate host truth, review truth, merge-ready truth, closeout truth, task carriers, or generated skills surfaces.

## Scope

- Add negative contract fixtures around `loom suite scaffold` dry-run and apply.
- Pre-seed forbidden truth surfaces and assert their content remains unchanged.
- Assert scaffold `planned_writes` and `created_locators` stay limited to the allowed `.loom/specs/<item>/` scaffold artifacts.
- Preserve existing #1114-#1117 scaffold behavior.

## Non-Goals

- No host integration or GitHub issue, Project, or PR writes.
- No review, merge-ready, closeout, task-carrier, generated skills, runtime attempt, or shadow truth writes.
- No new scaffold artifacts.
- No rollback execution command.
- No `/speckit.*` command names or `.specify/` layout.

## Acceptance Criteria

- AC-1118-1: Full-suite dry-run leaves forbidden truth surfaces and the target tree unchanged.
- AC-1118-2: Minimal apply creates only `spec.md` and `plan.md` for the requested item and leaves forbidden truth surfaces unchanged.
- AC-1118-3: Full apply creates only the six standard full-suite scaffold artifacts and leaves forbidden truth surfaces unchanged.
- AC-1118-4: Scaffold JSON does not emit host/review/merge-ready/closeout/generated-skill action keys.
- AC-1118-5: Contract tests continue to pass without changing the established `suite scaffold` CLI behavior.

## Guardrails

- CLI output remains evidence only; it does not replace Work Item truth, recovery truth, review records, merge-ready evidence, closeout evidence, or docs/source contracts.
- Existing generated skills/reference drift remains owned by the skills surface workflow.
