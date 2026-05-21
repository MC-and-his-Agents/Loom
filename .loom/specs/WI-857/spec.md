# WI-857 Spec

## Outcome

Loom's own Python compile validation compiles the repository entrypoints without writing `__pycache__` or Python bytecode into the checked-out repository or formal worktree.

## Acceptance

- A single repo-local py_compile wrapper compiles Python files while writing bytecode only to a temporary location that is cleaned up.
- The GitHub `loom-check` workflow consumes the cache-clean py_compile entrypoint.
- `make py-compile` is the documented local Python compile entrypoint and is included in `make check`.
- `loom_check` has a targeted cache hygiene fixture that compiles `src/skills/shared/scripts` and `skills/shared/scripts` and fails if new repository cache artifacts appear.
- The PR template points validation authors to the cache-clean compile entrypoint.
- Existing #817 installed runtime `.loom/bin` cache ignore/guard behavior remains intact.

## Non Goals

- Do not commit Python bytecode or cache directories.
- Do not make `.gitignore` the only solution for repository-local cache hygiene.
- Do not redesign validation, installer, or runtime governance outside #857.
- Do not reopen or alter the completed #856 middle capability aggregation result.
