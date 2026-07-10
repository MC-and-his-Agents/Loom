# Spec

## User Story

As an adopted repository using the global Loom CLI with metadata-only payload, I can refresh current carrier and shadow evidence without being required to commit a repo-local bootstrap manifest that the installation contract forbids.

## Acceptance

- `carrier refresh` skips bootstrap manifest reads and writes only when installed-state declares both `runtime_provider=global-cli` and `repo_payload.mode=metadata-only`.
- Current init-result and per-surface shadow source hashes remain consumable and refreshable.
- Repo-local runtime profiles keep the existing bootstrap manifest validation.
- Current-head semantic review remains required and cannot be refreshed away.

## Non-goals

- No WebEnvoy product changes.
- No required-check bypass.
- No broader v0.29 carrier or profile migration.

