# WI-1120 Spec

## Goal

Implement the core read-only `loom suite validate` command.

## Scope

- Add `suite validate` to the help JSON command matrix.
- Reuse the existing suite inspect state as the validate read model.
- Emit the standard `loom-cli-output/v1` envelope with `pass`, `block`, `advisory`, or `not_applicable`.
- Include `failed_layer`, `fail_closed_reason`, `missing_inputs`, `blocking_gaps`, `advisory_gaps`, and consumed contract locators.
- Keep the command read-only.

## Non-Goals

- No scaffold writes.
- No host, issue, PR, Project, review, merge-ready, or closeout writes.
- No generated skills synchronization.
- No `flow spec-review` integration.
- No `/speckit.*` command names or `.specify/` layout.

## Acceptance Criteria

- AC-1120-1: `loom help --json` declares `suite validate` as an implemented suite command.
- AC-1120-2: Missing suite path decisions fail closed with a blocking gap.
- AC-1120-3: Minimal and complete full suite fixtures pass core validation.
- AC-1120-4: `not_applicable` suite path decisions return `not_applicable` without mutation.
- AC-1120-5: Core advisory gaps are represented without upgrading deferred evidence/carrier work to blocking.
- AC-1120-6: Missing required artifacts fail closed with `missing_required_artifact`.

## Guardrails

- CLI output remains evidence only; it does not replace Work Item truth, recovery truth, review records, merge-ready evidence, closeout evidence, or docs/source contracts.
- Deeper validation remains owned by #1121-#1125.
