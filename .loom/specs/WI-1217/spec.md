# WI-1217 Spec

## Suite Contract

- Suite path: minimal
- Work Item / FR locator: #1217 / #1218-#1226
- Path decision provenance: #1217 is a bounded metadata-only adoption iteration over installation taxonomy, installed-state, CLI mode split, diagnostics, skills provider contracts, docs, fixtures, and release decision evidence.
- Full-suite-artifacts not_applicable: rationale: the work has an explicit issue tree and concrete command/fixture evidence; consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, target branch validation, issue closeout, and release/no-release decision consume this minimal suite plus Work Item evidence; recheck condition: promote to full suite if this expands into destructive migration apply, new host-private registration semantics, or a profile system.

## Scope

Make metadata-only repository adoption a first-class Loom mode where repository truth records adoption metadata and user-level Codex Loom plugin provides the skills/provider surface, while embedded repository payload mode remains explicitly supported.

## Scenarios

- S1: `loom install --mode metadata-only --target <fixture> --apply --json` writes only `.loom/installed-state.json` and does not create `plugins/loom/skills`, `.agents/skills`, or root `skills`.
- S2: Metadata-only installed-state declares `repo_payload.mode = metadata-only`, a user-scoped skills provider, intentional absence of repo skills payload, and no `plugin-embedded-skills` layer.
- S3: `loom installed-state validate`, `loom host verify --mode metadata-only`, `loom skills check`, and `loom detect` validate metadata-only fixtures without requiring embedded skills.
- S4: Unexpected repo embedded skills payload under metadata-only mode is diagnosed as an unexpected surface.
- S5: Embedded payload mode remains available through `loom host install --mode plugin` and continues to require `plugins/loom/skills`.
- S6: README, Codex install docs, unified install docs, host adapter matrix, installed-state docs, CLI matrix, taxonomy docs, and plugin manifest agree on metadata-only default, embedded opt-in, and user workstation authority boundaries.

## Acceptance Criteria

- AC-1: Installation taxonomy documents artifact type, scope, authority, skills granularity, repository adoption modes, and runtime carrier categories in one authoritative adoption document.
- AC-2: Metadata-only installed-state validates without `plugins/loom/skills`, `.agents/skills`, or root `skills`.
- AC-3: CLI install/host verify/skills check/detect support metadata-only mode and keep embedded payload mode strict.
- AC-4: User-level Codex plugin provider is modeled as workstation truth, not repository truth.
- AC-5: Docs and manifest do not imply `.agents/skills`, root `skills`, or repo-embedded `plugins/loom/skills` are universal defaults.
- AC-6: Regression evidence covers metadata-only, unexpected embedded payload pollution, and embedded payload compatibility.
- AC-7: Required checks pass locally and on PR/target branch before issue closeout and release/no-release decision.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: this batch is constrained to installation contracts, CLI mode semantics, diagnostics, docs, fixtures, and root governance carriers; consumer boundary: no separate research or external API contract artifact is required for this bounded change; recheck condition: require full suite artifacts if the work changes release publishing mechanics, destructive repair ownership, or host-private Codex registration semantics.
