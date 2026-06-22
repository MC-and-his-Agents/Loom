# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: `.loom/specs/WI-1714/spec.md`
  - Scenario ids / locators: S1, S2, S3 in `.loom/specs/WI-1714/spec.md`
  - Acceptance ids / locators: A1-A4 in `.loom/specs/WI-1714/spec.md`
  - Story Readiness consumed state: N/A
  - Story Business Confirmation consumed state: N/A
- Produces:
  - Validation strategy by scenario: focused Python unit test plus package checker surface.
  - Test strategy by acceptance: `test/plugin_payload_hash_test.py` and `tools/check_npm_package.py`.
  - Fresh verification evidence expectation: latest validation summary in `.loom/progress/WI-1714.md`.
- Locator:
  - Plan locator: `.loom/specs/WI-1714/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: GitHub issue #1714 and `.loom/specs/WI-1714/spec.md`
  - Freshness rule: re-run validation after any code, docs, test, or payload change in this PR.

## Implementation Goal

- Add deterministic plugin payload hash generation to `tools/check_npm_package.py`.
- Add a targetable `plugin-payload-hash` package validation surface and include it in aggregate package validation.
- Document the release evidence label and add focused tests for hash semantics.

## Deferred Items

### Release Metadata Writeback

- Locator: #1713
- Reason: #1714 only produces and validates the hash; manifest metadata generation is a separate release metadata work item.
- Activation condition: #1713 consumes the hash surface and writes release-bound metadata.
- Does not currently block: #1714 package hash generation.
- Statement: deferred is not completed.

## N/A Items

### Host Source/Cache Readback

- Locator: #1721
- Rationale: source/cache freshness readback requires host plugin metadata consumption after metadata exists.
- Recheck condition: when #1721 implements cache/source readback.
- Consumer boundary: #1714 review, merge-ready, and closeout should not require host source/cache readback.

## Phases

### Phase 1

- Objective: Implement deterministic hash helper and validation surface.
- Deliverable: `tools/check_npm_package.py` exposes `plugin-payload-hash`.
- Exit condition: targeted package surface passes.

### Phase 2

- Objective: Add regression coverage and release evidence docs.
- Deliverable: `test/plugin_payload_hash_test.py` and release evidence label update.
- Exit condition: unit test, package aggregate, release-doc contract, and fact-chain suite validation pass.

## Constraints

- Architectural or governance constraints: do not write plugin metadata or version bump in #1714.
- Workspace / rollout constraints: issue-scoped worktree `/Users/mc/dev/Loom-WI-1714-plugin-payload-hash`, branch `work/1714-plugin-payload-hash`.
- Purity or scope constraints: no host cache writes, no npm publish, no legacy installer behavior change.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 test/plugin_payload_hash_test.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`
  - `python3 tools/check_release_surface.py --surface release-doc-contract`
- Manual checks: inspect output for `plugin_payload_hash`, file count, and declared hash status.
- Runtime evidence: N/A; package validation is local deterministic validation.
- Behavior evidence: unit test and package checker output.
- Story scenario to evidence mapping: N/A; issue-derived scenarios are mapped below.
- Story readiness consumed: N/A.
- Story business confirmation locator: N/A.
- Scenario validation mapping:
  - S1 -> automated: `test/plugin_payload_hash_test.py`
  - S2 -> automated: `test/plugin_payload_hash_test.py`
  - S3 -> structural: `tools/check_npm_package.py --surface plugin-payload-hash`
- Fresh verification evidence: `.loom/progress/WI-1714.md`
- Execution ledger plan locator: `.loom/specs/WI-1714/plan.md`
- Execution ledger validation evidence locator: `.loom/progress/WI-1714.md`

## Test Strategy

- TDD or test-first expectation: add focused regression tests before merge-ready.
- Regression coverage to add or preserve: hash content sensitivity, order stability, ignored cache artifacts, aggregate package surface.
- Cases that are intentionally not automated: future manifest metadata writeback; #1713 owns it.
- How passing tests or equivalent checks will be captured as test evidence: validation summary and evidence map.
- Acceptance test mapping:
  - A1 -> test evidence
  - A2 -> test evidence
  - A3 -> test evidence
  - A4 -> structural check

## Subagent Output Integration

- Owned outputs: none; #1714 implementation is main-thread owned.
- Integration owner: main agent.
- Required evidence from each subagent: N/A.
- Review or reconciliation needed before merge-ready: semantic review and PR metadata readback.
- Handoff notes locator: N/A.

## Dependencies

- Blocking inputs: #1712 contract merged.
- Required coordination: #1713 consumes this hash surface for metadata writeback.
- Rollback boundary: revert #1714 PR without affecting host plugin command boundaries or skill contract version changes.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly N/A
- [x] Story business semantics are confirmed or explicitly N/A
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or N/A
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has N/A rationale and recheck condition
- [x] Risks and dependencies are explicit
