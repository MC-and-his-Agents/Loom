# WI-1914 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1914 is a release and milestone closeout convergence item after FR-1 through FR-5 implementation and closeout have already merged; consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, release readback, issue closeout, Phase closeout, and milestone closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if #1914 expands into new runtime behavior, release workflow mutation, credentials handling, or a second release/migration track.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1914
  - Parent Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1888
  - Milestone locator: https://github.com/MC-and-his-Agents/Loom/milestone/25
  - Completed FR locators: #1889, #1893, #1897, #1902, #1908.
  - Story Readiness consumed state: non-applicability recorded because this is a release convergence item governed by the accepted v0.27.0 issue tree; consumer boundary: review, PR gate, release readback, issue closeout, Phase closeout, and milestone closeout consume #1888/#1914 plus closed FR issues as the governing scope; recheck condition: require story readiness if new product behavior is added after the release bump.
  - Story Business Confirmation consumed state: non-applicability recorded because the milestone/FR issue tree defines the accepted product scope; consumer boundary: release PR review, release readback, and closeout consume the GitHub issue tree as business confirmation; recheck condition: require business confirmation if release scope changes beyond #1914.
- Produces:
  - Scenario ids / locators: S1 version authority, S2 pre-release validation, S3 post-merge release readback and closeout.
  - Acceptance ids / locators: A1-A5 below.
  - Behavior evidence expectation: release readiness evidence plus release/package/readback validation.
- Locator:
  - Spec locator: `.loom/specs/WI-1914/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1888, #1889, #1893, #1897, #1902, #1908, #1914, and this thread's release planning.
  - Freshness rule: rerun release/package validation after any VERSION, package, plugin metadata, release evidence, PR metadata, hosted checks, merge commit, or release readback change.

## Goal

Publish Loom `v0.27.0` after the Workstation Upgrade and Repo Slimdown milestone implementation has merged and closed out.

The release must align root version authority, npm package metadata, Codex plugin payload metadata/hash, release readiness evidence, PR metadata, hosted checks, GitHub Release, npm readback, and final issue/milestone closeout.

## Scope

- In scope:
  - Bump `VERSION` to `v0.27.0`.
  - Bump root `package.json` to `0.27.0`.
  - Stamp `plugins/loom/.codex-plugin/plugin.json` source package version, plugin payload version, pending release SHA, and payload hash.
  - Add `docs/evidence/v0.27.0-release-readiness.md`.
  - Add WI-1914 release carriers and review evidence.
  - Reconcile stale WI-1900 progress checkpoint to its existing terminal closeout metadata so the release gate has one active WI-1914 workspace owner.
  - Open and merge a release PR, then rely on the main-push `loom-cli-release` workflow for tag, GitHub Release, and npm publish.
  - Run release readback and close #1914, Phase #1888, and milestone #25 only after release evidence is consistent.
- Out of scope:
  - New CLI behavior beyond already merged FR-1 through FR-5 PRs.
  - New WI-1900 runtime or carrier behavior beyond terminal checkpoint reconciliation.
  - New release workflow behavior, credentials handling, or release automation rewrite.
  - Plugin surface version bump.
  - Skills registry or skill contract version bump.
  - Legacy `@mc-and-his-agents/loom-installer` release.
  - Manual tag overwrite, manual npm republish, or bypassing release workflow/readback.

## Key Scenarios

### Scenario S1

Given FR-1 through FR-5 implementation and closeout PRs are merged

When the release branch updates version authority and package/plugin payload metadata

Then `VERSION`, `package.json`, plugin source package version, plugin payload version, and plugin payload hash all describe the `v0.27.0` candidate consistently.

### Scenario S2

Given release metadata and readiness evidence are committed

When pre-release checks run on the release PR

Then release/package/suite/fact-chain/PR metadata/hosted gates pass without publishing from the PR event.

### Scenario S3

Given the release PR is merged

When the main-push release workflow publishes `v0.27.0`

Then release readback proves the tag, GitHub Release, npm package, workflow run, and package/plugin metadata all bind to the release merge commit before #1914, #1888, and milestone #25 are closed.

## Behavior Evidence

- Story scenario mapping: release-only Work Item consumes the v0.27.0 milestone issue tree and release surface contracts.
- Story readiness consumed state: no separate story readiness artifact is required because #1888/#1914 and the closed FR issue tree define release scope; review, PR gate, release readback, issue closeout, Phase closeout, and milestone closeout consume the issue tree as readiness input only for this release Work Item; require story readiness if new product scope is added.
- Story business confirmation consumed state: no separate business confirmation artifact is required because the milestone issue tree is the accepted business scope; release PR review, release readback, and final closeout consume the issue tree as business confirmation only for this release Work Item; require business confirmation if release scope changes beyond #1914.
- Scenario coverage:
  - S1 -> `VERSION`, `package.json`, `plugins/loom/.codex-plugin/plugin.json`
  - S2 -> `docs/evidence/v0.27.0-release-readiness.md` and validation summary
  - S3 -> post-merge `loom release readback --version v0.27.0`
- Expected evidence locator: `.loom/specs/WI-1914/evidence-map.md`
- Freshness rule: refresh validation after release metadata, PR body, review, hosted checks, merge commit, or release readback changes.
- Execution ledger acceptance locator: `.loom/progress/WI-1914.md`

## Exceptions And Boundaries

- Failure modes:
  - If `v0.27.0` tag/npm/GitHub Release already exists on a different commit, fail closed and do not overwrite.
  - If npm publish or GitHub Release is missing after merge, use the release workflow repair/readback path; do not manually invent evidence.
  - If plugin payload hash drifts, restamp metadata and rerun package checks before review.
- Operational boundaries:
  - PR event checks are read-only for release publication.
  - Main push workflow owns publication.
  - Closeout only follows successful release readback.
- Rollback or fallback expectations:
  - Before merge, revert the release branch changes.
  - After merge, never delete or overwrite published artifacts without an explicit release repair decision.

## Acceptance Criteria

- [ ] A1: `VERSION`, `package.json`, and plugin payload metadata all agree on `v0.27.0` / `0.27.0`.
- [ ] A2: Release readiness evidence names the #1888/#1889/#1893/#1897/#1902/#1908/#1914 scope and release boundaries.
- [ ] A3: Pre-release checks pass on the release PR without publishing.
- [ ] A4: Post-merge release readback proves tag, GitHub Release, npm package, workflow run, and package surface are consistent.
- [ ] A5: #1914, #1888, and milestone #25 close only after repo carrier closeout is terminalized.
