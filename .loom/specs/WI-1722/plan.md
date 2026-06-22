# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: `.loom/specs/WI-1722/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: not required
  - Story Business Confirmation consumed state: not required
- Produces:
  - Validation strategy by scenario: targeted installer tests, docs sync check, distribution check, suite/fact-chain checks, and diff hygiene.
  - Test strategy by acceptance: Node installer regression tests plus TypeScript compile.
  - Fresh verification evidence expectation: `.loom/progress/WI-1722.md` and `.loom/progress/WI-1722-build-evidence.json`
- Locator:
  - Plan locator: `.loom/specs/WI-1722/plan.md`
- Provenance:
  - Source issue: https://github.com/MC-and-his-Agents/Loom/issues/1722
  - Freshness rule: refresh after any installer source/test/docs/carrier change.

## Implementation Goal

Deliver the smallest installer change that retires single-skill user-visible success:

- Keep legacy `skill` CLI parsing for migration diagnostics.
- Return blocked diagnostics for `add`, `upgrade-plan`, and `verify-upgrade` skill mode.
- Stop emitting `generated-single-skill` as a current distribution layer.
- Keep `skill_package_version` readable only through old status metadata diagnostics.
- Add regression coverage proving no target mutation and no upgrade success.

## Deferred Items

- None. Release, publish, root CLI provider behavior, and host freshness/reporting are out of scope, not deferred completion for WI-1722.

## Skipped Items

- High-cost guardian: not required for this bounded installer worker lane unless main control requests it.
- Shared `.loom/status/current.md` / bootstrap carrier writes: skipped to avoid clobbering parallel #1713/#1721 control surfaces.
- Root README broad install copy: forbidden by worker scope.
- Version bump, npm publish, installer tag, or GitHub Release: forbidden by #1722 ownership.

## Phases

### Phase 1

- Objective: Implement fail-closed single-skill diagnostics.
- Deliverable: installer source and package README/test changes.
- Exit condition: `npm --prefix packages/loom-installer test` passes.

### Phase 2

- Objective: Bind behavior evidence to WI-1722 carriers.
- Deliverable: WI-1722 work item, progress, build evidence, minimal suite, evidence map, and task carrier.
- Exit condition: fact-chain, suite validate, suite evidence validate, and suite carrier validate pass for WI-1722.

### Phase 3

- Objective: Publish worker lane for review.
- Deliverable: final validation, commit, push, and PR opened for main control.
- Exit condition: PR URL and clean pushed branch are returned to the controller.

## Constraints

- Write ownership is limited to `packages/loom-installer/**`, directly related installer tests/docs, and WI-1722 Loom carriers.
- Forbidden surfaces: `tools/loom.py`, `plugins/loom/.codex-plugin/plugin.json`, `plugins/loom/**` release metadata/hash, root README broad marketing/install copy, version bump, npm publish, GitHub release, #1713, #1721, #1715, and unrelated legacy compatibility read-path deletion.
- Do not restore or recommend single SKILL install as a current install path.
- Do not make `skill_package_version` participate in freshness or upgrade success.

## Validation

- Automated checks:
  - `npm --prefix packages/loom-installer test`
  - `npm --prefix packages/loom-installer run check:docs`
  - `npm --prefix packages/loom-installer run check:distribution`
  - `git diff --check`
  - `python3 tools/loom.py fact-chain --target . --item WI-1722 --json`
  - `python3 tools/loom.py suite validate --target . --item WI-1722 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1722 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1722 --json`
- Manual checks:
  - `git status --short`
  - forbidden-surface diff review
- Runtime evidence: not required; no live host writes or external-visible actions.
- Scenario validation mapping:
  - S1 -> automated test evidence: installer regression tests.
  - S2 -> automated test evidence: legacy metadata diagnostic regression test.
  - S3 -> automated test evidence: TypeScript compile and installer regression tests consume the direct function no-copy implementation.
- Fresh verification evidence: `.loom/progress/WI-1722.md`

## Test Strategy

- Regression coverage is updated in `packages/loom-installer/test/installer.test.ts`.
- Existing installer test command rebuilds payload and compiles TypeScript before running tests.
- No package version bump is allowed for this worker lane.
- No browser, host profile, or live runtime test is needed because this change avoids external host writes.
- Acceptance mapping:
  - A1 -> test evidence: Codex and Claude single-skill add fail closed.
  - A2 -> test evidence: `legacy-single-skill-diagnostic` replaces current `generated-single-skill` output.
  - A3 -> test evidence: old status metadata produces incompatible diagnostic.
  - A4 -> test evidence: `skill_package_version` remains absent from available version context and old persisted metadata is not rewritten.
  - A5 -> test evidence: `npm --prefix packages/loom-installer test`.

## Subagent Output Integration

- Owned outputs: none; no true subagent tool was available in this environment.
- Integration owner: main executor.
- Required evidence from each subagent: not required.
- Review or reconciliation needed before merge-ready: current-head review is required later by main control.
- Handoff notes locator: final worker response.

## Dependencies

- Blocking inputs: GitHub issue #1722 and baseline `origin/main` at `48bfd6e546e2393f8bc4f5b8de90a14aaa2e9405`.
- Required coordination: avoid #1713/#1721 host/plugin metadata and #1715 freshness surfaces.
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
