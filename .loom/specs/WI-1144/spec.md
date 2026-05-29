# Spec

## Suite Contract

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: #1144 is a packaging/release surface alignment Work Item and does not define new user-facing suite behavior; consumer boundary: package, release-check, CLI contract, and closeout may consume this minimal suite evidence without treating skipped full path artifacts as completed; recheck condition: #1144 starts changing suite validation semantics, publish workflow semantics, or release authority.
- Consumes:
  - Work Item / FR locator: #1144 / #1136
  - Story Readiness source: GitHub Work Item body is the scoped carrier.
  - Story scenario source: scenarios are authored below.
  - Story Business Confirmation source: governance behavior only, with no business-semantics carrier.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A4 in this file.
  - Behavior evidence expectation: release/package checks fail closed if suite source-truth docs are missing from the root CLI package or if release-check skips package validation.
- Locator:
  - Spec locator: .loom/specs/WI-1144/spec.md
- Provenance:
  - Source issue / PR / doc locator: #1144, #1136, docs/methodology/harness/full-spec-suite-cli-surface.md, docs/adoption/loom-cli-release-surface.md, docs/adoption/version-authority-map.md
  - Freshness rule: re-run package, release, version, CLI contract, and npm smoke checks after changing package or release-check surfaces.

## Goal

- Keep root `loom` distribution checks aligned with full spec suite CLI automation.
- Ensure installed/npm runtime payloads include suite source-truth docs needed by suite commands and closeout consumers.

## Scope

- In scope: root package manifest payload, npm package checker required files, `loom skills release-check` package validation, CLI contract assertion, and npm package smoke assertion.
- Out of scope: publishing a release, changing `VERSION`, changing installer legacy behavior, or adding new suite command semantics.

## Key Scenarios

### Scenario S1

Given
- suite automation depends on Loom docs/source truth for suite, evidence, carrier, gate-chain, and GitHub profile contracts

When
- `python3 tools/check_npm_package.py` validates the root `loom` npm package

Then
- the checker requires those suite contract docs to be listed in `package.json` and present in `npm pack --dry-run` output.

### Scenario S2

Given
- release-check is the aggregate distribution preflight surface for generated skills and runtime payloads

When
- `loom skills release-check --json` runs

Then
- it consumes `tools/check_npm_package.py` in addition to host adapter, version, release, and skills surface checks.

### Scenario S3

Given
- a maintainer changes package metadata

When
- npm smoke tests run

Then
- they assert the root package includes suite contract source-truth docs before package/install surface changes can pass.

## Behavior Evidence

- Story scenario mapping: S1-S3 are issue-scoped and authored in this file.
- Story readiness locator: #1144 body is the readiness source.
- Story business confirmation locator: none required for this governance-only behavior.
- Scenario coverage:
  - S1 -> expected behavior evidence locator: `tools/check_npm_package.py`.
  - S2 -> expected behavior evidence locator: `tools/loom.py` `skills release-check` checks list and `tools/check_cli_contract.py`.
  - S3 -> expected behavior evidence locator: `test/npm-package-smoke.test.mjs`.
- Expected evidence locator: .loom/specs/WI-1144/evidence-map.md
- Freshness rule: evidence is fresh only after local package/release/contract checks pass on the current head.
- Execution ledger acceptance locator: .loom/progress/WI-1144.md
- Behavior-bearing change rationale: distribution checks now guard suite source-truth package payload.

## Exceptions And Boundaries

- Failure modes: missing package docs, missing npm pack payload, release-check skipping package validation, version authority drift, and release surface drift fail closed in their existing owners.
- Operational boundaries: this Work Item does not publish npm, create tags, create GitHub Releases, or modify host truth.
- Rollback or fallback expectations: revert package/checker/release-check additions and rerun package plus release surface checks.

## Acceptance Criteria

- [x] A1: Root `package.json` includes suite source-truth docs needed by suite automation.
- [x] A2: `tools/check_npm_package.py` requires those docs in both manifest and `npm pack --dry-run` payload.
- [x] A3: `loom skills release-check --json` consumes `tools/check_npm_package.py` and reports its result.
- [x] A4: CLI contract and npm smoke tests fail if release-check/package surface stops consuming the package payload guard.
