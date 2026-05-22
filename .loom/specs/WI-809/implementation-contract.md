# WI-809 Implementation Contract

## Allowed Change Surface

- `src/skills/shared/scripts/governance_surface.py`
- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/shared/references/adoption/github-profile-upgrade.md`
- Generated `skills/**/.loom-runtime/shared/scripts/governance_surface.py`
- Generated `skills/**/.loom-runtime/shared/scripts/loom_flow.py`
- Generated `skills/**/.loom-runtime/shared/scripts/loom_check.py`
- Generated `skills/**/.loom-runtime/shared/references/adoption/github-profile-upgrade.md`
- `skills/shared/scripts/governance_surface.py`
- `skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_check.py`
- `skills/shared/references/adoption/github-profile-upgrade.md`
- `examples/new-project/.loom/bin/governance_surface.py`
- `examples/new-project/.loom/bin/loom_flow.py`
- `examples/new-project/.loom/bin/loom_check.py`
- `docs/adoption/github-profile-upgrade.md`
- `docs/evidence/fixtures/github-profile-maturity-fixtures.json`
- Installer package version files when generated `skills/` payload changes
- Loom Work Item, progress, spec, review, and status carriers for `WI-809`

## Required Properties

- Detector reads existing Loom and GitHub-profile signals only.
- Missing or conflicting required signals must fail closed into a blocked judgment.
- `blocked` must not become a maturity level value.
- Upgrade status and upgrade-plan outputs must carry source locators that explain the judgment.
- Fixture validation must cover light, standard, strong, and blocked cases.

## Exit Criteria

- PR #880 is bound to `WI-809` and #809.
- Local validation and GitHub PR checks pass.
- PR #880 merges to `main`.
- #809 and Project #4 are synchronized with PR/merge closeout evidence.
