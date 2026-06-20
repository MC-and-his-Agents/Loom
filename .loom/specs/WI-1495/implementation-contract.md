# WI-1495 Implementation Contract

## Scope

- Add retained closeout resolver fixtures that prefer canonical `WI-<issue>` identity binding.
- Keep downstream adoption guidance scoped to metadata-only host repository carriers plus global CLI / Codex user-level plugin usage.
- Preserve generated skill/reference mirror consistency for closeout gate and host action contract guidance.

## Non Goals

- Do not add repo-local runtime, plugin, or skills installation paths.
- Do not restore single-skill package distribution.
- Do not add legacy installer compatibility.
- Do not change release behavior.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 test/retained_item_lookup_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 test/work_item_audit_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `git diff --check`
