# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: `.loom/specs/WI-1732/spec.md`
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: not required for this issue-scoped tombstone package change
  - Story Business Confirmation consumed state: not required for this issue-scoped tombstone package change
- Produces:
  - Validation strategy by scenario: tombstone package test, docs check, run-regression, release-surface guard, diff hygiene, and Loom carrier checks.
  - Test strategy by acceptance: one Node test proves fail-closed JSON migration output; structural checks cover CI/release guard.
  - Fresh verification evidence expectation: `.loom/progress/WI-1732.md`
- Locator:
  - Plan locator: `.loom/specs/WI-1732/plan.md`
- Provenance:
  - Source spec / issue: `.loom/specs/WI-1732/spec.md`, GitHub issue #1732
  - Freshness rule: refresh after package, workflow, guard, or carrier changes.

## Implementation Goal

Convert `packages/loom-installer` from active installer code to a tombstone package with one fail-closed CLI result and one regression test.

## Deferred Items

- None.

## Out Of Scope Items

- `npm deprecate`: external-visible release closeout action; not part of this implementation PR.
- Root Loom v0.19.0 release: handled by release closeout issue #1718.

## Phases

### Phase 1

- Objective: Remove active installer behavior.
- Deliverable: tombstone CLI, README, scripts, CI, and release-surface guard.
- Exit condition: targeted local checks pass.

### Phase 2

- Objective: Bind evidence and prepare PR.
- Deliverable: WI-1732 carriers, review, PR metadata, hosted checks.
- Exit condition: controlled merge and closeout pass.

## Constraints

- Do not restore single-skill or legacy plugin install behavior.
- Do not execute `npm deprecate` in this implementation PR.
- Do not publish or tag non-v0.19.0 release artifacts.

## Validation

- Automated checks:
  - `npm --prefix packages/loom-installer test`
  - `npm --prefix packages/loom-installer run check:docs`
  - `node packages/loom-installer/scripts/run-regression.mjs`
  - `python3 tools/check_release_surface.py --surface installer-sunset-guard`
  - `git diff --check`
  - Loom fact-chain, suite, evidence, and carrier validations
- Runtime evidence: not required; no live npm or host writes.
- Scenario validation mapping:
  - S1 -> automated validation: tombstone package test.
  - S2 -> structural validation: workflow diff and installer sunset guard.
  - S3 -> manual evidence: README / issue wording; final npm deprecate confirmation is deferred to release closeout.

## Test Strategy

- One Node test is enough because every CLI invocation returns the same tombstone result.
- No active installer fixtures remain.
- Acceptance validation mapping:
  - A1 -> test evidence: `packages/loom-installer/test/installer.test.ts` confirms fail-closed CLI result.
  - A2 -> test evidence: `packages/loom-installer/test/installer.test.ts` confirms migration command points to root Loom CLI and `loom host ...`.
  - A3 -> structural check: `.github/workflows/node-installer-pr.yml`, `.github/workflows/node-installer-release.yml`, and `tools/check_release_surface.py --surface installer-sunset-guard`.
  - A4 -> structural check: `packages/loom-installer/README.md` and `packages/loom-installer/README.zh-CN.md`.
  - A5 -> structural check: README release-closeout wording plus `tools/check_release_surface.py --surface installer-sunset-guard`.

## Subagent Output Integration

- Owned outputs: none
- Integration owner: main executor
- Handoff notes locator: none

## Dependencies

- Blocking inputs: GitHub issue #1732.
- Required coordination: release closeout #1718 must separately confirm `npm deprecate`.
- Rollback boundary: this branch only.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is not required for this issue-scoped tombstone package change
- [x] Story business semantics are not required for this issue-scoped tombstone package change
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
