# WI-851 Plan

## Steps

1. Add a versioned Governance Lint negative fixture manifest with all eight required bypass categories.
2. Extend `loom_check.py` with a fixture contract checker that validates taxonomy, consumers, synthetic source mode, no temporary truth carrier, and supporting advanced/hardcoding fixture files.
3. Add installed runtime negative checks for PR body approval text, CI-success-only merge, and stale review/head drift, building on existing raw-only and `spec_review` fixtures.
4. Sync generated skills surface and bump installer patch version because shared runtime behavior changed.
5. Validate with py_compile, targeted fixture contract, skills surface check, installer version bump check, diff check, full `loom_check.py`, fact-chain, and checkpoint merge.

## Evidence Plan

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY' ... check_governance_lint_negative_fixture_contract ... PY`
- `python3 tools/skills_surface.py check`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-851`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py checkpoint merge --target . --item WI-851`

## Rollback

Revert the new fixture manifest, `loom_check.py` fixture additions, generated skills surface, and installer version bump, then rerun `tools/loom_check.py` to restore the prior fixture surface.
