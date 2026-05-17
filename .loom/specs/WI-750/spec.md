# WI-750 Spec

## Objective

Switch Loom review runs to use `loom/codex-app-review` by default only inside a verified Codex App interactive host, while preserving `loom/default-codex` as the safe default for CI, headless, missing proof, and unavailable app-server paths.

## Acceptance Criteria

- Explicit `--engine-adapter` continues to take precedence over automatic selection.
- Non-CI runs with complete App proof select `loom/codex-app-review` by default.
- CI or `CODEX_CI` runs select `loom/default-codex` even when thread identifiers are present.
- Missing or unavailable App host proof falls back to `loom/default-codex` and records the fallback reason.
- Conflicting App proof, mismatched cwd/root, unverifiable reviewed head, target binding failure, or normalization failure fail closed.
- App proof includes endpoint, thread id, thread cwd proof, target root, and reviewed head; `thread_cwd` must equal `target_root`.
- Live app-server review starts against the current thread and consumes only `exitedReviewMode.review`; normalization uses the same app-server thread's `turn/start.outputSchema`.
- Raw App review evidence remains runtime evidence only and cannot satisfy merge-ready approval without the authored review record.
- `engine_metadata` records selected adapter, selection source, fallback reason, app-server endpoint, thread id, thread cwd, target root, reviewed head, review thread id, raw review locator, normalized findings locator, and context pack locator.
- `review_record_input.engine_adapter` and reviewer match the selected adapter.
- `skills/` and `src/skills/` generated and source surfaces stay synchronized.
- Installer behavior version truth is bumped because distributed skill behavior changed.

## Validation

- `python3 -m py_compile tools/loom_flow.py tools/loom_check.py skills/shared/scripts/*.py src/skills/shared/scripts/*.py`
- `python3 tools/loom_check.py`
- `make check`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `python3 tools/version_surface_check.py`
