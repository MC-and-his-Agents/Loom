# WI-1121 Spec

## Goal

Validate suite path decisions and required/conditional suite artifacts before later formal spec gates consume them.

## Scope

- Detect missing, invalid, or conflicting suite path decisions.
- Keep legal path decisions limited to `full`, `minimal`, and `not_applicable`.
- Treat full path required artifacts as `suite-index.md`, `spec.md`, and `plan.md`.
- Treat minimal path required artifacts as `spec.md` and `plan.md`.
- Block required artifacts that are missing, directories, symlinks, or otherwise not ordinary files.
- Include full path conditional artifacts in artifact inventory without enforcing rationale in this Work Item.

## Non-Goals

- No not_applicable/deferred rationale enforcement.
- No spec to plan mapping validation.
- No final failure taxonomy expansion beyond the existing #1052 failure kinds already consumed by #1120.
- No `flow spec-review` or `gate spec-review` integration.
- No host, issue, PR, Project, review, merge-ready, or closeout writes from `loom suite validate`.
- No `/speckit.*` command names or `.specify/` layout.

## Acceptance Criteria

- AC-1121-1: Conflicting suite path decision fixtures fail closed.
- AC-1121-2: Invalid path decision carriers fail closed without selecting a suite path.
- AC-1121-3: Missing full path required artifacts continue to block.
- AC-1121-4: Required artifact directories or symlinks block as required artifact gaps.
- AC-1121-5: Full path conditional artifacts are represented in inventory as conditional and absent when not present.
- AC-1121-6: Minimal and complete full fixtures that satisfy required artifacts continue to pass.

## Guardrails

- CLI output remains evidence only; it does not replace Work Item truth, recovery truth, review records, merge-ready evidence, closeout evidence, or docs/source contracts.
- Deeper validation remains owned by #1122-#1125.
