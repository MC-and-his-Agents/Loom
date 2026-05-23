# WI-873 Spec

## Problem

Repo-specific PR metadata currently depends on free-form Markdown. That makes parser behavior ambiguous, hides field-level diagnostics, and lets review/merge-ready gates lose the distinction between an absent block, a malformed block, and missing repo-specific fields.

## Goals

- Define a Loom core machine carrier contract for repo companion PR metadata without importing any downstream field taxonomy.
- Support an HTML comment JSON block as the first machine carrier type.
- Add parser preflight with fail-closed diagnostics for malformed or incomplete machine blocks.
- Preserve migration compatibility so old PRs are advisory by default unless a repo declares required blocking behavior.
- Wire the preflight into PR review and merge-ready consumption points.

## Non-Goals

- Do not add WebEnvoy-specific field names or taxonomy to Loom core.
- Do not make free-form Markdown the machine truth source.
- Do not require old PRs to fail when the companion remains in advisory migration mode.

## Acceptance

- `metadata_contract.fields[*].machine_carrier` validates carrier type, schema version, marker, required repo fields, preflight, diagnostics, and migration mode.
- `pr-metadata preflight` parses PR payloads and reports block locator, parse error, missing fields, expected format, and suggested fix.
- Invalid machine blocks block; absent blocks follow `migration_mode`.
- `pr-gate check` and `flow merge-ready` consume blocking metadata preflight results when declared.
- `loom_check` covers valid, malformed, missing-field, absent advisory, absent required, forbidden truth-field, and unsafe locator cases.
