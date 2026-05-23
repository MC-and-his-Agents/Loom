# WI-873 Plan

## Implementation Steps

1. Extend the repo companion metadata contract validator to accept a bounded `machine_carrier` object.
2. Implement PR body HTML comment JSON extraction, envelope validation, diagnostics, and migration handling in `loom_flow.py pr-metadata preflight`.
3. Add `pr_metadata_preflight` to `pr-gate check` and `flow merge-ready` with a stable failure taxonomy entry.
4. Add focused `loom_check` fixtures for valid and failing parser/preflight cases.
5. Update adoption and harness documentation, then regenerate shared skill/runtime surfaces with `tools/skills_surface.py generate`.
6. Validate with py_compile, generated surface checks, full `make check`, `loom_check`, diff whitespace checks, and direct CLI fixture checks.

## Rollback

- Revert the runtime preflight integration and contract validator changes together.
- Keep migration mode advisory as the compatibility fallback if downstream repo companion declarations need staged adoption.

## Evidence

- Local validation is recorded in `.loom/progress/WI-873.md`.
- PR #982 binds the implementation branch to issue #873.
