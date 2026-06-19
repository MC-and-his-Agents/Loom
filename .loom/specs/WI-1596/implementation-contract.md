# WI-1596 Implementation Contract

## Ownership

- Version authority: `VERSION`, `package.json`, and `skills/*/loom-package.json`.
- Release evidence: `docs/evidence/v0.15.0-release-readiness.md`.
- Loom carriers: `WI-1596` work item/progress/review/status/shadow/spec files and WI-1598 terminal carrier metadata.

## Forbidden Scope

- Do not alter `.github/workflows/loom-cli-release.yml` semantics.
- Do not alter npm package payload inclusion/exclusion semantics outside version metadata.
- Do not publish, dispatch release workflow with `publish=true`, or merge the release PR without explicit authorization.
- Do not close #1594 before all milestone #13 issues and release evidence are terminal.

## Release Boundary

The release PR is publish-capable because `VERSION`, `package.json`, and skill package metadata change to v0.15.0. The expected publish mechanism is the existing `loom-cli-release` main-push workflow after authorized merge.
