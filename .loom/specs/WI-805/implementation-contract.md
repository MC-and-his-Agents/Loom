# WI-805 Implementation Contract

## Allowed Change Surface

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- Generated `skills/**/.loom-runtime/shared/scripts/loom_flow.py`
- Generated `skills/**/.loom-runtime/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_check.py`
- `examples/new-project/.loom/bin/loom_flow.py`
- `examples/new-project/.loom/bin/loom_check.py`
- `docs/evidence/fixtures/safe-sync-plan-fixtures.json`
- Safe sync harness docs under `docs/methodology/harness/`
- Installer package version files when generated `skills/` payload changes
- Loom Work Item, progress, spec, review, status, and shadow carriers for `WI-805`

## Required Properties

- Dry-run must never report or execute applied host actions.
- Non-dry-run must execute only audited `planned_actions`.
- Planned action kinds must remain a small stable set.
- Missing proof and block findings must fail closed into skipped/manual actions.
- Fixture validation must cover both write-producing and write-blocking paths.

## Exit Criteria

- PR #878 is bound to `WI-805` and #805/#806/#807.
- Local validation and GitHub PR checks pass.
- PR #878 merges to `main`.
- #805/#806/#807 and parent #804 are synchronized with PR/Project closeout evidence.
