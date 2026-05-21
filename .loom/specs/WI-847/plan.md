# WI-847 Plan

## Steps

1. Tighten implementation approval consumption so only `general_review` or `code_review` records with `decision: allow` can satisfy implementation approval.
2. Add a machine-readable `approval_boundary` and `governance_lint` section to `pr-gate check`.
3. Extend installed runtime fixtures to prove raw-only evidence and `spec_review` records fail closed.
4. Sync generated skills surface from `src/skills`.
5. Validate with py_compile, skills surface check, version bump check, `git diff --check`, and full `tools/loom_check.py`.

## Evidence Plan

- `python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py checkpoint merge --target . --item WI-847`

## Rollback

Revert the PR-gate approval-boundary output and fixture additions, then rerun `tools/loom_check.py` to confirm prior PR gate behavior is restored.
