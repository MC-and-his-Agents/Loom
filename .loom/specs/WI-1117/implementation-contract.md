# WI-1117 Implementation Contract

## Owned Surface

- Contract-test assertions for `loom suite scaffold` JSON audit fields.

## Required Fields

- `planned_writes`
- `source_templates`
- `overwrite_policy`
- `apply_required`
- `rollback_note`
- `created_locators`

## Required Behavior

- Dry-run remains read-only.
- Apply creates only missing scaffold artifacts.
- Existing files are preserved.
- `created_locators` reports only files actually created.
- Ambiguous overwrite or non-file artifact placeholders fail closed before partial writes.
- Rollback guidance remains descriptive and does not become an executable rollback surface.

## Forbidden Surface

- No `/speckit.*` command names.
- No `.specify/` layout.
- No generated skills, host writes, review writes, merge-ready writes, or closeout writes.
