# WI-810 Implementation Contract

## Allowed Change Surface

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_check.py`
- Generated `skills/**/.loom-runtime/shared/scripts/loom_flow.py`
- Generated `skills/**/.loom-runtime/shared/scripts/loom_check.py`
- `docs/adoption/github-profile-upgrade.md`
- Loom Work Item, progress, spec, review, and status carriers for `WI-810`

## Required Properties

- `upgrade-plan` is read-only and dry-run by default.
- `blocked` remains a maturity judgment concept and does not become a maturity level.
- Repo-owned review instruction locators are declared through companion contracts, not guessed from repo-specific filenames.
- GitHub controlled merge is represented as host-controlled evidence and host object targets, not as Loom-owned merge implementation.
- Companion generation previews or records companion artifacts without producing repo-native shadow verdicts.

## Exit Criteria

- PR is bound to `WI-810` and #810.
- Local validation and GitHub PR checks pass.
- PR merges to `main`.
- #810 and Project #4 synchronize with PR/merge closeout evidence.
