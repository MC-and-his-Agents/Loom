# WI-1294 Spec

## Suite Contract

- Suite path: minimal
- Work Item / FR locator: #1294 / #1217 / #1227
- Path decision provenance: #1294 is a bounded release follow-up after #1227 merged metadata-only adoption changes but the post-merge `loom-cli-release` push run failed closed because `v0.13.9` already points at another commit.
- Full-suite-artifacts not_applicable: rationale: the work is limited to root Loom CLI version surfaces, generated skill package `repo_version` metadata, release checks, PR/CI, and post-merge publish evidence; consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, target branch validation, #1217 correction evidence, and #1294 closeout consume this minimal suite plus Work Item evidence; recheck condition: promote to full suite if this expands into release workflow semantics, package naming, installer release behavior, or metadata-only runtime behavior changes.

## Scope

Publish the #1217/#1227 metadata-only adoption CLI and skills changes by advancing the root Loom CLI release candidate from occupied `v0.13.9` to unpublished `v0.13.10`.

## Scenarios

- S1: `VERSION` is `v0.13.10`, `package.json` is `0.13.10`, and generated `skills/*/loom-package.json` `repo_version` fields match `v0.13.10`.
- S2: Local release, version, package, CLI, npm dry-run, and skills surface checks accept the `v0.13.10` release candidate without metadata-only behavior changes.
- S3: The follow-up PR merges to `main` and `loom-cli-release` publishes or verifies `v0.13.10` tag, GitHub Release, and npm package evidence for the merge commit.
- S4: #1217 and #1294 closeout evidence records that #1227's `v0.13.9` publish failed closed correctly and the follow-up release completed through `v0.13.10`.

## Acceptance Criteria

- AC-1: Root version authority is advanced to `v0.13.10` / `0.13.10`.
- AC-2: Generated skill package `repo_version` metadata is synchronized.
- AC-3: Release/version/package/CLI/skills checks pass locally and in PR CI.
- AC-4: Main `loom-cli-release` succeeds after merge and publishes or verifies `v0.13.10`.
- AC-5: #1217 and #1294 contain final release evidence and #1294 is closed.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: this batch is a release candidate bump and evidence closeout, not a new behavior implementation; consumer boundary: no separate research, readiness checklist, contracts, or suite index artifact is required for this bounded release follow-up; recheck condition: require full suite artifacts if the work changes release workflow mechanics, metadata-only adoption behavior, or installer publishing behavior.
