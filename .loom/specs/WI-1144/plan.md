# Plan

## Suite Contract

- Suite path consumed: minimal
- Full suite artifact skip is consumed from .loom/specs/WI-1144/spec.md.
- Consumes:
  - Spec locator: .loom/specs/WI-1144/spec.md
  - Scenario ids / locators: S1-S3 in .loom/specs/WI-1144/spec.md
  - Acceptance ids / locators: A1-A4 in .loom/specs/WI-1144/spec.md
  - Story Readiness consumed state: #1144 issue body
  - Story Business Confirmation consumed state: skipped for governance-only behavior
- Produces:
  - Validation strategy by scenario: package payload, release-check aggregation, CLI contract, and npm smoke assertions.
  - Test strategy by acceptance: focused package/release checks plus full CLI contract checks.
  - Fresh verification evidence expectation: .loom/progress/WI-1144.md
- Locator:
  - Plan locator: .loom/specs/WI-1144/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1144/spec.md, #1144
  - Freshness rule: update validation summary after final local checks.

## Implementation Goal

- Make the root `loom` release/package preflight prove suite source-truth docs are shipped with the npm package.
- Make the aggregate release-check consume package dry-run evidence before reporting release surface pass.

## Future Items

### Future Item 1

- Locator: #1145 E2E governance test FR
- Reason: broad E2E fixtures are owned by #1145, not this package-surface Work Item.
- Activation condition: when #1107 reaches FR #1145.
- Does not currently block: #1144 package/release surface alignment.
- Statement: this future item is not completed by #1144.

## Skipped Items

### Skipped Item 1

- Locator: release publish workflow execution
- Rationale: #1144 validates release/package surfaces but does not publish a release or change `VERSION`.
- Recheck condition: if package or release workflow behavior changes beyond validation coverage.
- Consumers that should not require it: #1144 closeout.

## Phases

### Phase 1

- Objective: Add package payload coverage for suite source-truth docs.
- Deliverable: `package.json` manifest entries and `tools/check_npm_package.py` required manifest/pack-file checks.
- Exit condition: package checker passes and reports suite docs in required payload.

### Phase 2

- Objective: Add aggregate release-check coverage.
- Deliverable: `loom skills release-check` runs package checker; CLI contract asserts the check is consumed.
- Exit condition: release-check JSON includes `tools/check_npm_package.py`.

### Phase 3

- Objective: Preserve install/package smoke behavior.
- Deliverable: npm smoke test asserts suite contract docs remain in package manifest.
- Exit condition: node package smoke passes.

## Constraints

- Architectural or governance constraints: release/version/package checks are evidence; they do not replace Work Item, review, merge-ready, closeout, Project, or docs/source truth.
- Workspace / rollout constraints: issue-scoped branch/worktree/PR only.
- Purity or scope constraints: no external command names or layout, no unrelated packaging refactor, no release publish.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_npm_package.py tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --json`
  - `node --test test/npm-package-smoke.test.mjs`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
  - `git diff --check`
  - focused `rg` for package/release-check and forbidden external command/layout strings
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Manual checks: inspect `loom skills release-check --json` checks list and package checker required files.
- Runtime evidence: .loom/progress/WI-1144.md
- Behavior evidence: tools/check_npm_package.py; tools/check_cli_contract.py; test/npm-package-smoke.test.mjs
- Scenario validation mapping:
  - S1 -> automated: package checker required files and npm pack payload.
  - S2 -> automated: release-check JSON plus CLI contract assertion.
  - S3 -> automated: npm package smoke manifest assertion.
- Fresh verification evidence: .loom/progress/WI-1144.md
- Execution ledger plan locator: .loom/specs/WI-1144/plan.md
- Execution ledger validation evidence locator: tools/check_npm_package.py; tools/check_cli_contract.py; test/npm-package-smoke.test.mjs

## Test Strategy

- TDD or test-first expectation: package/release-check assertions are added with the implementation because the existing checks currently pass while missing this coverage.
- Regression coverage to add or preserve: package payload docs, release-check checker list, npm smoke manifest docs, existing release/version surface checks.
- Cases that are intentionally not automated: live npm publish and GitHub Release creation, because #1144 does not publish.
- How failing tests or equivalent checks will be introduced before implementation: existing `loom skills release-check --json` lacked `tools/check_npm_package.py`; new CLI contract assertion would fail on the previous implementation.
- How passing tests or equivalent checks will be captured as test evidence: focused package/release checks and full CLI contract.
- Acceptance test mapping:
  - A1 -> automated: package.json manifest diff plus node package smoke.
  - A2 -> automated: tools/check_npm_package.py manifest and npm pack output.
  - A3 -> automated: loom skills release-check JSON output.
  - A4 -> automated: tools/check_cli_contract.py and node package smoke.
- How User Story acceptance scenarios map to tests, checks, or manual validation: S1-S3 and A1-A4 map to the automated and structural checks above.

## Subagent Output Integration

- Owned outputs: main executor owns implementation.
- Integration owner: main executor.
- Required evidence from each subagent: none; current multi-agent tool requires explicit user authorization before spawning.
- Review or reconciliation needed before merge-ready: spec review, implementation review, PR gate, closeout.
- Handoff notes locator: not required; recovery entry remains .loom/progress/WI-1144.md.

## Dependencies

- Blocking inputs: #1144 issue body, full spec suite CLI surface, release surface docs, version authority map, package manifest.
- Required coordination: parent FR #1136 and phase #1107 progress comments after closeout.
- Rollback boundary: revert package/checker/release-check assertions only.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed by #1144 issue scope
- [x] Story business semantics are skipped because this is governance-only behavior
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
