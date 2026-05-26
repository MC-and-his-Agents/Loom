# WI-1069 Spec

## Objective

Add root `loom` CLI npm publish automation to the existing `loom-cli-release` workflow.

## Acceptance Criteria

- Pull requests run release-surface, version, CLI contract, npm package contract, and npm dry-run checks without publishing.
- Push or manual publish paths can create the GitHub `v*` tag, publish `@mc-and-his-agents/loom`, and create the GitHub Release only when CLI publish behavior changed or publish is explicitly requested.
- The workflow fails closed when `VERSION`, `package.json`, existing tag state, GitHub Release state, or npm version state is inconsistent.
- A real npm publish requires `NPM_TOKEN`; missing auth fails before publication.
- The workflow does not reactivate `loom-installer` publishing and does not bump `VERSION`.
