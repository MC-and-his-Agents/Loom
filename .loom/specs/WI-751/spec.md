# WI-751 Spec

## Goal

Complete phase 4 of #746 by removing the ambiguous `loom/default-codex` adapter name from current Codex review adapter contracts and by proving the release/merge gate still consumes only the single authored review record.

## Acceptance Criteria

- Current runtime and generated skill surfaces use `loom/codex-app-review` for verified Codex App review mode and `loom/default-codex-exec` for the exec-hosted fallback.
- Current documentation and skill references describe fallback, fail-closed behavior, manual review, and raw evidence boundaries with the same adapter vocabulary.
- Checker fixtures validate App default selection, exec fallback, manual fallback, cwd mismatch/proof conflict, schema drift, stale review head behavior, and raw evidence bypass protection.
- Merge-ready and PR gate continue to require the authored `review_entry`; raw Codex App output and shadow evidence cannot satisfy approval truth.
- Parent issue #746 is not closed until #751 is merged, post-merge validation passes, and all child stage issues are read back as complete/closed.

## Non-Goals

- Do not reopen or rework #750 phase 3 behavior beyond the adapter vocabulary cleanup required by #751.
- Do not add a second review truth source or let merge-ready consume engine raw output directly.
- Do not remove headless/CI `codex exec --output-schema` fallback behavior.
- Do not expand Loom into a multi-engine marketplace.
