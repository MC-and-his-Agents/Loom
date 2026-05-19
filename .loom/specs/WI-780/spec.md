# WI-780 Spec

## Problem

Default Loom adoption currently treats target repository release/version truth as if a bootstrap release exists. That creates example `.loom/companion/releases/**` carriers and can make downstream verification consume placeholder release state instead of repo-owned truth.

## Required Behavior

- New adoption must not generate `.loom/companion/releases/**` by default.
- `repo-interface.json` must omit `release_targets` unless the target repository explicitly declares release target intent.
- Absent release targets must verify as `release_targets.availability = absent` and `target_release.result = not_applicable`.
- Governance surface entries for absent `catalog`, `current_target`, and `status` must not report `present`.
- Existing explicit repo-owned release target validation remains supported.

## Out Of Scope

- Adding a new release target intent CLI.
- Promoting downstream release, guardian, project, or review rules into Loom core.
- Changing attach-only, light-governance, or execution-control carrier boundaries beyond release target absence.
