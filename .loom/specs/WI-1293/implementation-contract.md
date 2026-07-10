# WI-1293 Implementation Contract

## Ownership

- Version authority: `VERSION`, `package.json`, and `skills/*/loom-package.json`.
- User documentation and CLI/help surface: `README.md`, `README.zh-CN.md`, `docs/adoption/**`, `docs/methodology/harness/cli-command-matrix.md`, and `tools/loom.py` command matrix summaries.
- Release evidence: `docs/evidence/v0.16.0-release-readiness.md`.
- Loom carriers: WI-1293 work item/progress/review/status/shadow/spec files.

## Forbidden Scope

- Do not alter `.github/workflows/loom-cli-release.yml` semantics.
- Do not alter npm package payload inclusion/exclusion semantics outside version metadata.
- Do not change #1452 controlled-merge runtime logic or #1292 fixture logic.
- Do not mutate live branch protection/rulesets.
- Do not edit external HotCP/WebEnvoy/Syvert repositories.
- Do not close #1285 before #1293 release evidence is terminal.

## Release Boundary

The release PR is publish-capable because `VERSION`, `package.json`, and skill package metadata change to v0.16.0. The expected publish mechanism is the existing `loom-cli-release` main-push workflow after authorized merge.
