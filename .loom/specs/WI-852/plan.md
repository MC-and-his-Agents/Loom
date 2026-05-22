# WI-852 Plan

## Steps

1. Reuse the existing Governance Lint status builder for `status` and `merge_ready` surfaces.
2. Wire `flow merge-ready` to emit and consume the lint envelope through a deterministic `governance-lint` step.
3. Wire `loom_status` to expose the lint envelope and map blocking lint into status classifications and missing inputs.
4. Preserve authored truth boundaries: review records, checkpoint payloads, host checks, and PR body text remain separate from lint evidence.
5. Extend `loom_check.py` to validate status and merge-ready lint envelopes, step ordering, installed runtime behavior, and stale-status negative fixtures.
6. Regenerate the checked-in skills surface and bump the installer package version.
7. Validate with py_compile, skills surface check, focused daily execution / Governance Lint fixture checks, version bump check, and full `tools/loom_check.py`.

## Evidence Plan

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_status.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_status.py skills/shared/scripts/loom_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
- focused `check_daily_execution_cli` and `check_governance_lint_negative_fixture_contract`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py flow merge-ready --target examples/new-project --item INIT-0001`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_status.py --target examples/new-project --item INIT-0001`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py .`

## Rollback

Revert the `flow merge-ready` lint step, `loom_status` lint exposure, `loom_check.py` assertions, output contract edits, installer version bump, generated skills surface, and WI-852 carriers, then rerun the focused status / merge-ready smoke and skills surface check.
