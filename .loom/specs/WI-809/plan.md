# WI-809 Plan

## Steps

1. Add GitHub profile maturity detector support to the governance profile runtime.
2. Preserve the existing maturity level enum and add a separate maturity judgment that can report blocked.
3. Add fixture coverage for light, standard, strong, and blocked judgments.
4. Update the GitHub profile upgrade adoption contract and shared references.
5. Teach `loom_check` to validate the GitHub profile maturity fixture contract.
6. Regenerate checked-in skills/runtime surfaces and demo runtime.
7. Bind PR #880 to WI-809 and refresh merge gate carriers.
8. Validate locally and through GitHub PR checks before merge/closeout.

## Validation

- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py ...`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `python3 tools/version_surface_check.py`
- `python3 tools/host_adapter_check.py`
- GitHub profile maturity fixture smoke
- governance-profile status/upgrade-plan/upgrade smoke
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py`
- GitHub PR checks
