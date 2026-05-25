# WI-1006 Spec

## Intent

Move Loom install, release, and version authority documentation to a single active `loom` CLI line and demote `loom-installer` to deprecated legacy evidence.

## Scope

- Root English and Chinese README install and release sections.
- `docs/adoption/loom-cli-release-surface.md`
- `docs/adoption/version-authority-map.md`
- `docs/adoption/codex-install.md`
- `packages/loom-installer/README.md`
- `packages/loom-installer/README.zh-CN.md`
- Doc-sync and release/version surface checker needles needed to keep the documentation contract aligned.
- Skills distribution contract wording that still describes the installer as a fixed active adapter surface.

## Required Behavior

- Default installation documentation recommends full repository install plus native or host skill discovery.
- `loom` CLI is described as the only active CLI release line.
- `loom-installer` is described as a deprecated legacy artifact, not the current CLI, recommended install path, active release line, or CLI release evidence.
- `loom-installer-v0.1.119` and npm `0.1.119` are retained only as legacy baseline evidence.
- English and Chinese public README surfaces stay synchronized.

## Non-Goals

- Do not deprecate the npm package in this work item.
- Do not enable automatic `loom` CLI publishing in this work item.
- Do not add a new npm package, Homebrew formula, or standalone binary.
- Do not rewrite historical validation evidence.
