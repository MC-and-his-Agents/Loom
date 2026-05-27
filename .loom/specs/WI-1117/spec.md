# WI-1117 Spec

## Goal

Define and verify scaffold overwrite, rollback, and created locator JSON audit fields for `loom suite scaffold`.

## Scope

- Assert `planned_writes`, `source_templates`, `overwrite_policy`, `apply_required`, `rollback_note`, and `created_locators` for minimal and full scaffold paths.
- Assert ambiguous overwrite handling is represented as fail-closed evidence.
- Assert fail-closed overwrite or non-file artifact scenarios do not create partial scaffold artifacts.
- Preserve the existing scaffold behavior from #1114, #1115, and #1116.

## Non-Goals

- No automatic rollback command.
- No new scaffold artifacts.
- No host, review, merge-ready, closeout, generated skill, `/speckit.*`, or `.specify/` mutation surfaces.

## Acceptance Criteria

- AC-1117-1: Minimal dry-run JSON includes explicit rollback, overwrite, planned write, source template, apply-required, and empty created locator fields.
- AC-1117-2: Minimal apply JSON reports actual created locators and rollback guidance.
- AC-1117-3: Existing scaffold files are preserved and reported in `overwrite_policy.existing_files`.
- AC-1117-4: Ambiguous overwrite or non-file artifact placeholders fail closed before any write and keep `created_locators` empty.
- AC-1117-5: Full suite dry-run/apply JSON carries the same audit fields for all six standard artifacts.
- AC-1117-6: Contract tests cover the schema fields without changing #1114-#1116 behavior.

## Guardrails

- CLI output remains evidence only; it does not replace Work Item truth, recovery truth, review records, merge-ready evidence, closeout evidence, or docs/source contracts.
- Do not copy spec-kit `/speckit.*` command names or `.specify/` layout.
