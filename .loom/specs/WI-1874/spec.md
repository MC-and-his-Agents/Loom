# WI-1874 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1874 is a release-only convergence slice with implementation scope already merged through #1869 / PR #1875 and is reviewable through spec, plan, implementation contract, evidence map, release readiness evidence, package validation, and release readback; consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, release readback, issue closeout, parent closeout, and milestone closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if this work expands into new runtime behavior, release workflow mutation, credentials handling, or multi-release migration.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1874
  - Implementation parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1869
  - Implementation PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1875
  - Story Readiness consumed state: non-applicability recorded because this is a release convergence item for the already merged #1869 implementation tree; consumer boundary: review, PR gate, release readback, and closeout consume #1869/#1874 as the governing scope; recheck condition: require story readiness if new product behavior is added after #1869.
  - Story Business Confirmation consumed state: non-applicability recorded because milestone #24 and #1869 define the accepted product scope; consumer boundary: review, PR gate, release readback, and closeout consume the GitHub issue tree as business confirmation; recheck condition: require business confirmation if release scope changes beyond #1869/#1874.
- Produces:
  - Scenario ids / locators: S1 version authority, S2 release evidence, S3 post-merge readback and closeout.
  - Acceptance ids / locators: A1-A5 below.
  - Behavior evidence expectation: release readiness evidence plus release/package/readback validation.
- Locator:
  - Spec locator: `.loom/specs/WI-1874/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1874, #1869, PR #1875, milestone #24.
  - Freshness rule: rerun release/package validation after any VERSION, package, plugin metadata, release evidence, or carrier change.

## Goal

Publish Loom `v0.26.1` after the #1869 closeout recovery polish implementation has merged.

The release must align root version authority, npm package metadata, Codex plugin payload metadata/hash, release readiness evidence, PR metadata, hosted checks, GitHub Release, npm readback, and final Loom carrier closeout.

## Scope

- In scope:
  - Bump `VERSION` to `v0.26.1`.
  - Bump `package.json` to `0.26.1`.
  - Stamp `plugins/loom/.codex-plugin/plugin.json` source package version, plugin payload version, pending release SHA, and payload hash.
  - Add `docs/evidence/v0.26.1-release-readiness.md`.
  - Add WI-1874 release carriers and review evidence.
  - Open and merge a release PR, then rely on the main-push `loom-cli-release` workflow for tag, GitHub Release, and npm publish.
  - Run release readback and close #1869/#1874 plus milestone #24 only after release evidence is consistent.
- Out of scope:
  - New CLI behavior beyond the already merged #1869 implementation.
  - New gate scheduling system or multi-command rewrite.
  - Plugin surface version bump.
  - Skills registry or contract version bump.
  - Legacy `@mc-and-his-agents/loom-installer` release.
  - Manual tag overwrite, manual npm republish, or bypassing release workflow/readback.

## Key Scenarios

### Scenario S1

Given the #1869 implementation PR is merged to `main`

When the release branch updates version authority and package/plugin payload metadata

Then `VERSION`, `package.json`, plugin source package version, plugin payload version, and plugin payload hash all describe the `v0.26.1` candidate consistently.

### Scenario S2

Given release metadata and readiness evidence are committed

When pre-release checks run on the release PR

Then release/package/suite/fact-chain/PR metadata/hosted gates pass without publishing from the PR event.

### Scenario S3

Given the release PR is merged

When the main-push release workflow publishes `v0.26.1`

Then release readback proves the tag, GitHub Release, npm package, workflow run, and package/plugin metadata all bind to the release merge commit before issues and milestone are closed.

## Behavior Evidence

- Story scenario mapping: release-only Work Item consumes #1869 implementation scope and release surface contracts.
- Scenario coverage:
  - S1 -> `VERSION`, `package.json`, `plugins/loom/.codex-plugin/plugin.json`
  - S2 -> `docs/evidence/v0.26.1-release-readiness.md` and validation summary
  - S3 -> post-merge `loom release readback --version v0.26.1`
- Expected evidence locator: `.loom/specs/WI-1874/evidence-map.md`
- Freshness rule: refresh validation after release metadata, PR body, review, hosted checks, merge commit, or release readback changes.
- Execution ledger acceptance locator: `.loom/progress/WI-1874.md`

## Exceptions And Boundaries

- Failure modes:
  - If `v0.26.1` tag/npm/GitHub Release already exists on a different commit, fail closed and do not overwrite.
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

- [ ] A1: `VERSION`, `package.json`, and plugin payload metadata all agree on `v0.26.1` / `0.26.1`.
- [ ] A2: Release readiness evidence names the #1869/#1874 scope and release boundaries.
- [ ] A3: Pre-release checks pass on the release PR without publishing.
- [ ] A4: Post-merge release readback proves tag, GitHub Release, npm package, workflow run, and package surface are consistent.
- [ ] A5: #1869/#1874 and milestone #24 close only after repo carrier closeout is terminalized.
