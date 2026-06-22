# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: `.loom/specs/WI-1719/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: not required
  - Story Business Confirmation consumed state: not required
- Produces:
  - Validation strategy by scenario: targeted installer tests, docs sync check, suite/fact-chain checks, and diff hygiene.
  - Test strategy by acceptance: Node installer regression tests plus generated payload build assertions.
  - Fresh verification evidence expectation: `.loom/progress/WI-1719.md` and `.loom/progress/WI-1719-build-evidence.json`
- Locator:
  - Plan locator: `.loom/specs/WI-1719/plan.md`
- Provenance:
  - Source issue: https://github.com/MC-and-his-Agents/Loom/issues/1719
  - Freshness rule: refresh after any installer source/test/docs/carrier change.

## Implementation Goal

Deliver the smallest installer change that makes single SKILL version contract-only:

- Stop generating `skill_package_version` in current payload skill records.
- Stop placing `skill_package_version` in new single-skill version context.
- Stop comparing legacy `skill_package_version` in upgrade freshness.
- Preserve legacy metadata tolerance for migration diagnostics.
- Add regression coverage for old installed metadata.

## Deferred Items

- None. Release publication and broader CLI provider behavior are out of scope, not deferred completion for WI-1719.

## Skipped Items

- High-cost guardian: not required for this bounded installer slice unless hosted gates or review request it.
- PR metadata carrier: required for PR #1725 and already rendered/read back before review.
- Root release version bump, npm publish, installer tag, or installer GitHub Release: forbidden by #1719 ownership.
- Installer package metadata patch bump: allowed only to satisfy the existing `node-installer-pr` behavior-change admission gate; it does not authorize npm publish, installer tag creation, or installer GitHub Release.

## Phases

### Phase 1

- Objective: Implement contract-only single-skill version semantics.
- Deliverable: installer source, payload build script, and regression test changes.
- Exit condition: `npm --prefix packages/loom-installer test` passes.

### Phase 2

- Objective: Bind behavior evidence to Loom carriers.
- Deliverable: WI-1719 work item, progress, build evidence, minimal suite, task carrier, status, and bootstrap fact-chain entry.
- Exit condition: fact-chain, suite validate, suite evidence validate, and suite carrier validate pass for WI-1719.

### Phase 3

- Objective: Validate, publish, and review PR state.
- Deliverable: targeted checks, commit, push, PR metadata readback, review records, and merge-ready evidence.
- Exit condition: PR #1725 is merged and issue #1719 closeout passes.

## Constraints

- Write ownership is limited to `packages/loom-installer/**`, directly related installer tests/docs, and WI-1719 Loom carriers.
- Forbidden surfaces: `tools/check_npm_package.py`, `test/plugin_payload_hash_test.py`, host command boundary README/skills docs, root release version files, npm publish/release files, installer tag/release creation, and other worktrees.
- Do not restore or recommend single SKILL install as a current install path.
- Do not recommend legacy installer or full-repo clone.

## Validation

- Automated checks:
  - `npm --prefix packages/loom-installer test`
  - `npm --prefix packages/loom-installer run check:docs`
  - `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
  - `git diff --check`
  - `python3 tools/loom.py fact-chain --target . --item WI-1719 --json`
  - `python3 tools/loom.py suite validate --target . --item WI-1719 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1719 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1719 --json`
- Manual checks:
  - `git status --short`
  - forbidden-surface diff review
- Runtime evidence: not required; no live host writes or external-visible actions.
- Scenario validation mapping:
  - S1 -> automated test evidence: installer regression test.
  - S2 -> automated test evidence: installer regression test with injected legacy metadata.
  - S3 -> automated test evidence: installer payload build / manifest regression test.
- Fresh verification evidence: `.loom/progress/WI-1719.md`

## Test Strategy

- Regression coverage added in `packages/loom-installer/test/installer.test.ts`.
- Existing installer test command rebuilds payload and compiles TypeScript before running tests.
- Installer package metadata version bumps from `0.1.148` to `0.1.149` only because `node-installer-pr` requires a package version change when `packages/loom-installer/src/**` behavior changes; this is not release authorization.
- No separate browser, host profile, or live runtime test is needed because this change does not perform external host writes.
- Acceptance mapping:
  - A1 -> test evidence: single-skill install assertion.
  - A2 -> test evidence: legacy metadata upgrade-plan assertion.
  - A3 -> test evidence: payload manifest assertion.
  - A4 -> test evidence: `npm --prefix packages/loom-installer test`.
  - A5 -> structural check: suite/fact-chain carrier validation.

## Subagent Output Integration

- Owned outputs: none; main executor handled implementation and carrier updates serially.
- Integration owner: main executor.
- Required evidence from each subagent: not required.
- Review or reconciliation needed before merge-ready: current-head spec and implementation review records are required for PR #1725.
- Handoff notes locator: `.loom/progress/WI-1719.md`

## Dependencies

- Blocking inputs: GitHub issue #1719 and baseline #1712 merge commit.
- Required coordination: avoid #1714 main-thread and #1720 worker ownership; do not touch other worktrees.
- Rollback boundary: this branch only.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly not required
- [x] Story business semantics are confirmed or explicitly not required
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
