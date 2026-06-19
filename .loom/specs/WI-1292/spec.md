# Spec

## Suite Contract

- Suite path: minimal
- Suite index locator: .loom/specs/WI-1292/spec.md
- Consumes:
  - Work Item / FR locator: GitHub issue #1292; parent #1285
  - Completed dependency: GitHub issue #1452; PR #1614; merge commit b4199b2e4b623b8ad10cbb9dc6daeddaea52e8fc; carrier-sync PR #1637
  - Story Readiness: N/A
    - Locator: GitHub issue #1292
    - Rationale: #1292 has explicit fixture scope and acceptance criteria in the issue body.
    - Consumer boundary: spec review and implementation review may consume the issue body plus this minimal suite.
    - Recheck condition: require story shaping if scope expands beyond regression fixtures.
  - Story Business Confirmation: N/A
    - Locator: GitHub issue #1292
    - Rationale: this is internal harness regression coverage, not a new end-user workflow.
    - Consumer boundary: review and release notes may summarize the fixture coverage but do not redefine it.
    - Recheck condition: require confirmation if user-facing policy defaults or release behavior changes.
- Produces:
  - Scenario ids / locators: S1, S2, S3, S4 in this spec
  - Acceptance ids / locators: A1-A5 in this spec
  - Behavior evidence expectation: targeted CLI contract fixtures and hosted PR gate readback
- Locator:
  - Spec locator: .loom/specs/WI-1292/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1292; GitHub issue #1452; PR #1614; PR #1637
  - Freshness rule: valid for PR head that includes `tools/check_cli_contract.py` cross-repo review gate fixtures.

- Full suite artifacts not_applicable: rationale: WI-1292 is bounded to regression fixture coverage over existing gate behavior; consumer boundary: spec review, implementation review, merge-ready, and closeout consume the minimal suite plus targeted CLI evidence; recheck condition: expand to full suite if this work changes runtime gate contracts, live GitHub settings, release behavior, or shared adapter schema.

## Goal

- Add explicit HotCP/WebEnvoy/Syvert-style review and merge gate regression fixtures.
- Consume #1452 triggered-check controlled-merge behavior instead of reimplementing runtime product logic.

## Scope

- In scope:
  - `tools/check_cli_contract.py` fixture additions for HotCP-style post-merge review bypass, CI-only bypass, and stale/head drift.
  - WebEnvoy-style guardian triggered check failed/pending block through controlled-merge rollup.
  - Syvert-style guardian/integration advisory, conflict, and pending coverage.
  - `docs/evidence/fixtures/complex-existing-authority-migration-fixtures.json` inventory entries for downstream triggered-check consumption.
  - Targeted validation on the `controlled-merge` CLI contract surface.
- Out of scope:
  - Runtime product logic changes in `loom_flow.py`.
  - Live GitHub branch protection, ruleset, or required-check mutation.
  - #1293 release convergence and v0.16.0 publication.
  - Parent #1285 final closeout.

## Key Scenarios

### Scenario S1

Given a HotCP-style repository has green CI or a review recorded after merge

When PR gate evaluates merge readiness

Then CI-only and post-merge review evidence fail closed and expose repair diagnostics.

### Scenario S2

Given a HotCP-style PR head drifts after authored review

When PR gate evaluates the current head

Then stale review and head binding drift block merge readiness.

### Scenario S3

Given a WebEnvoy-style guardian check is triggered and fails or remains pending while required checks are green

When controlled-merge evaluates triggered checks

Then controlled-merge blocks on the guardian triggered-check rollup.

### Scenario S4

Given a Syvert-style guardian/integration signal is advisory, conflicting, or pending

When PR gate or controlled-merge evaluates merge readiness

Then advisory signals do not replace Loom semantic review, and conflicting or pending triggered verdicts block controlled merge.

## Acceptance Criteria

- [x] A1: HotCP-style post-merge review bypass is covered.
- [x] A2: HotCP-style CI-only bypass is covered.
- [x] A3: HotCP-style stale/head drift is covered.
- [x] A4: WebEnvoy-style guardian failed/pending blocks consume #1452 triggered-check behavior.
- [x] A5: Syvert-style guardian/integration advisory cannot replace Loom semantic review, and conflicting or pending triggered verdicts block controlled merge.
