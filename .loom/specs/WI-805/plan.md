# WI-805 Plan

## Steps

1. Add a safe sync plan envelope for reconciliation sync.
2. Make reconciliation sync dry-run by default and require `--apply` for host writes.
3. Add proof, write target, rollback, skipped, and manual action metadata.
4. Add fixtures for block findings, missing proof, close issue/comment, and Project Done plans.
5. Teach `loom_check` to validate the safe sync plan contract and dry-run applied action guard.
6. Update harness docs and regenerate checked-in skills/runtime surfaces.
7. Bind PR #878 to WI-805 and refresh merge gate carriers.
8. Validate locally and through GitHub PR checks before merge/closeout.

## Validation

- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py ...`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- safe sync fixture contract smoke
- reconciliation sync dry-run smoke
- `PYTHONDONTWRITEBYTECODE=1 make loom-check`
- GitHub PR checks
