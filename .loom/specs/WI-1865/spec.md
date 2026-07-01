# WI-1865 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1865 is a release-only convergence slice with implementation scope already merged through #1859 / PR #1866 and is reviewable through spec, plan, implementation contract, evidence map, release readiness evidence, package validation, and release readback; consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, release readback, issue closeout, parent closeout, and milestone closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if this work expands into new runtime behavior, release workflow mutation, credentials handling, or multi-release migration.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1865
  - Implementation parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1859
  - Implementation PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1866
  - Story Readiness consumed state: non-applicability recorded because this is a release convergence item for the already merged #1859 implementation tree; consumer boundary: review, PR gate, release readback, and closeout consume #1859/#1865 as the governing scope; recheck condition: require story readiness if new product behavior is added after #1859.
  - Story Business Confirmation consumed state: non-applicability recorded because milestone #23 and #1859 define the accepted product scope; consumer boundary: review, PR gate, release readback, and closeout consume the GitHub issue tree as business confirmation; recheck condition: require business confirmation if release scope changes beyond #1859/#1865.
- Produces:
  - Scenario ids / locators: S1 version authority, S2 release evidence, S3 post-merge readback and closeout.
  - Acceptance ids / locators: A1-A5 below.
  - Behavior evidence expectation: release readiness evidence plus release/package/readback validation.
- Locator:
  - Spec locator: `.loom/specs/WI-1865/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1865, #1859, PR #1866, milestone #23.
  - Freshness rule: rerun release/package validation after any VERSION, package, plugin metadata, release evidence, or carrier change.

## Goal

Publish Loom `v0.26.0` after the #1859 single-repo runtime-upgrade safe lane implementation has merged.

The release must align root version authority, npm package metadata, Codex plugin payload metadata/hash, release readiness evidence, PR metadata, hosted checks, GitHub Release, npm readback, and final Loom carrier closeout.

## Scope

- In scope:
  - Bump `VERSION` to `v0.26.0`.
  - Bump `package.json` to `0.26.0`.
  - Stamp `plugins/loom/.codex-plugin/plugin.json` source package version, plugin payload version, pending release SHA, and payload hash.
  - Add `docs/evidence/v0.26.0-release-readiness.md`.
  - Add WI-1865 release carriers and review evidence.
  - Open and merge a release PR, then rely on the main-push `loom-cli-release` workflow for tag, GitHub Release, and npm publish.
  - Run release readback and close #1859-#1865 plus milestone #23 only after release evidence is consistent.
- Out of scope:
  - New CLI behavior beyond the already merged #1859 implementation.
  - Multi-repo batching.
  - Plugin surface version bump.
  - Skills registry or contract version bump.
  - Legacy `@mc-and-his-agents/loom-installer` release.
  - Manual tag overwrite, manual npm republish, or bypassing release workflow/readback.

## Key Scenarios

### Scenario S1

Given the #1859 implementation PR is merged to `main`

When the release branch updates version authority and package/plugin payload metadata

Then `VERSION`, `package.json`, plugin source package version, plugin payload version, and plugin payload hash all describe the `v0.26.0` candidate consistently.

### Scenario S2

Given release metadata and readiness evidence are committed

When pre-release checks run on the release PR

Then release/package/suite/fact-chain/PR metadata/hosted gates pass without publishing from the PR event.

### Scenario S3

Given the release PR is merged

When the main-push release workflow publishes `v0.26.0`

Then release readback proves the tag, GitHub Release, npm package, workflow run, and package/plugin metadata all bind to the release merge commit before issues and milestone are closed.

## Behavior Evidence

- Story scenario mapping: release-only Work Item consumes #1859 implementation scope and release surface contracts.
- Scenario coverage:
  - S1 -> `VERSION`, `package.json`, `plugins/loom/.codex-plugin/plugin.json`
  - S2 -> `docs/evidence/v0.26.0-release-readiness.md` and validation summary
  - S3 -> post-merge `loom release readback --version v0.26.0`
- Expected evidence locator: `.loom/specs/WI-1865/evidence-map.md`
- Freshness rule: refresh validation after release metadata, PR body, review, hosted checks, merge commit, or release readback changes.
- Execution ledger acceptance locator: `.loom/progress/WI-1865.md`

## Exceptions And Boundaries

- Failure modes:
  - If `v0.26.0` tag/npm/GitHub Release already exists on a different commit, fail closed and do not overwrite.
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

- [ ] A1: `VERSION`, `package.json`, and plugin payload metadata all agree on `v0.26.0` / `0.26.0`.
- [ ] A2: Release readiness evidence names the #1859/#1865 scope and release boundaries.
- [ ] A3: Pre-release checks pass on the release PR without publishing.
- [ ] A4: Post-merge release readback proves tag, GitHub Release, npm package, workflow run, and package surface are consistent.
- [ ] A5: #1859-#1865 and milestone #23 close only after repo carrier closeout is terminalized.
