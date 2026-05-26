# WI-1068 Spec

## Acceptance

- Primary install/adoption docs fail closed if they present `loom-installer`, SKILLS, or plugins as independent primary/default/recommended install surfaces.
- Root npm package checks fail closed if `package.json` references the deprecated installer surface or omits CLI-managed `skills`, `src/skills`, or Codex plugin payload files.
- Existing release-surface separation remains intact: `loom-installer` can appear only as deprecated historical evidence, not active CLI publish evidence.
- The change remains checker scoped and does not add npm publish automation or reactivate installer publishing.

## Non-Goals

- Do not add or publish any npm package.
- Do not change the first npm CLI release workflow.
- Do not reactivate `loom-installer` release or migration journeys.
