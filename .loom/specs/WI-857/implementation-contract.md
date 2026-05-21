# WI-857 Implementation Contract

## Allowed Change Surface

- `tools/py_compile_clean.py`
- `Makefile`
- `.github/workflows/loom-check.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `src/skills/shared/scripts/loom_check.py`
- Generated `skills/**/loom_check.py` surfaces derived from `src/skills`
- Installer package version files when generated `skills/` payload changes
- Loom Work Item, progress, spec, review, and status carriers for `WI-857`

## Required Properties

- The wrapper must perform real Python compilation and fail on syntax errors.
- Bytecode output must be written outside the repository tree and cleaned automatically.
- `make py-compile` must cover both source and generated shared runtime scripts.
- `make check` must include `make py-compile`.
- `loom_check` must fail closed if the workflow returns to bare `python3 -m py_compile` or if wrapper execution creates repository cache artifacts.
- Existing runtime cache ignore rules for `.loom/bin/**/__pycache__/` and `.loom/bin/**/*.py[cod]` must remain in place.

## Exit Criteria

- PR is bound to `WI-857` and #857.
- Local and GitHub validation pass.
- PR merges to `main`.
- #857 is closed and Project #4 is Done.
