# WI-810 Plan

## Steps

1. Fix the GitHub profile adoption decision set used by `governance-profile upgrade-plan`.
2. Add repo-owned spec review and implementation review instruction locator judgments.
3. Give GitHub controlled merge explicit host write target locators.
4. Expand upgrade-plan output so every fixed judgment has read, judge, write, and verify steps.
5. Tighten `loom_check` validation so missing fixed judgments or missing phases fail.
6. Update the GitHub profile upgrade contract and regenerate the checked-in skills surface.
7. Validate with targeted upgrade-plan smoke, py_compile, skills surface check, and full Loom checks before PR merge.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py governance-profile upgrade-plan --target . --host github`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py governance-profile upgrade --target . --to strong --dry-run --host github`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py`
- GitHub PR checks
