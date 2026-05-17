# WI-751 Plan

## Steps

1. Read GitHub #751/#746 truth and establish a formal `WI-751` fact chain.
2. Rename the exec-hosted fallback adapter contract from `loom/default-codex` to `loom/default-codex-exec` in current runtime, checkers, docs, and generated skill surfaces.
3. Keep `loom/codex-app-review` behavior unchanged for verified App host default, explicit authoritative mode, and shadow comparison.
4. Refresh generated `skills/` surfaces from `src/skills/`.
5. Run focused validation, write fresh spec and implementation review records, then prove PR merge gate and controlled merge readiness.
6. After merge, read back `main`/`origin/main`, run post-merge validation, close #751 with evidence, verify all #746 child stages, then close #746 with parent closeout evidence.

## Validation

- `python3 tools/version_surface_check.py`
- `python3 -m py_compile tools/loom_flow.py tools/loom_check.py skills/shared/scripts/*.py src/skills/shared/scripts/*.py`
- `python3 tools/loom_check.py`
- `make check`
- `python3 tools/loom_flow.py pr-gate ...`
- `python3 tools/loom_flow.py controlled-merge ...`

## Risk Controls

- Preserve the single `review_entry` authored truth boundary.
- Treat historical review/runtime evidence as historical; current contracts and fixtures must use the cleaned adapter name.
- Fail closed if review head, validation summary, required checks, or branch protection readback drift.
