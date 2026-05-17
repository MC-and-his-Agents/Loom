# WI-751 Implementation Contract

## Runtime Contract

- `loom/codex-app-review` is the Codex App review adapter.
- `loom/default-codex-exec` is the exec-hosted fallback adapter backed by `codex exec --output-schema`.
- `review_record_input.reviewer` and `review_record_input.engine_adapter` must equal the actual selected adapter.
- Explicit `--engine-adapter` accepts only current authoritative adapter names.

## Fallback Contract

- CI/headless mode, missing App host proof, and unavailable live app-server fall back to `loom/default-codex-exec`.
- App proof conflicts, cwd/target/head mismatches, invalid raw output, and normalization/schema drift fail closed and point to manual review through the same `review_entry`.

## Evidence Contract

- Runtime evidence may include raw Codex App output, normalized findings, metadata, and context pack locators.
- Merge-ready and PR gate approval truth remains the authored review record only.
- Raw App output, shadow comparison output, CI success, and runtime evidence alone never satisfy approval truth.

## Synchronization Contract

- `src/skills/` is the generated surface source.
- `skills/` must be regenerated after source edits and checked with `python3 tools/skills_surface.py check`.
- Documentation under `docs/methodology/harness/review-execution.md` must stay aligned with `skills/shared/references/harness/review-execution.md` and `src/skills/shared/references/harness/review-execution.md`.
