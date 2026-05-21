# WI-857 Plan

## Steps

1. Add a cache-clean py_compile wrapper under `tools/`.
2. Route CI and local Makefile compile checks through the wrapper.
3. Add a `loom_check` fixture that proves wrapper execution does not create repository Python cache artifacts.
4. Update validation guidance so new PRs do not recommend bare `python3 -m py_compile`.
5. Regenerate the checked-in skills surface from `src/skills`.
6. Bump the installer patch version when the generated `skills/` payload changes.
7. Validate targeted cache hygiene, skills surface, host adapter, version surface, loom_check, installer version gate, and Git diff cleanliness.
8. Push PR, wait for checks, merge, then close out #857 and Project #4.

## Validation

- `make py-compile`
- targeted cache find scan before and after py_compile wrapper execution
- `python3 tools/skills_surface.py check`
- `python3 tools/version_surface_check.py`
- `python3 tools/host_adapter_check.py`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `git diff --check`
- `python3 tools/loom_check.py`
- GitHub PR checks
