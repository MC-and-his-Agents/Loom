# WI-1874 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1874 is a release-only convergence slice with a frozen implementation scope and is reviewable through spec, plan, implementation contract, evidence map, release readiness evidence, package validation, and release readback; consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, release readback, issue closeout, parent closeout, and milestone closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if this work expands into new runtime behavior, release workflow mutation, credentials handling, or multi-release migration.
- Consumes:
  - Spec locator: `.loom/specs/WI-1874/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
- Produces:
  - Validation strategy by scenario: version/package checks, release checks, hosted checks, release readback.
  - Test strategy by acceptance: release/package CLI checks plus post-merge readback.
  - Fresh verification evidence expectation: `.loom/progress/WI-1874.md` latest validation summary and release readiness document.
- Locator:
  - Plan locator: `.loom/specs/WI-1874/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: `.loom/specs/WI-1874/spec.md`, #1874.
  - Freshness rule: refresh after version, package, plugin metadata, release readiness, review, PR metadata, hosted checks, or release readback changes.

## Implementation Goal

Deliver the `v0.26.1` release candidate and prepare it for release workflow publication after merge.

Explicitly deferred until after merge: GitHub tag, GitHub Release, npm publish, release readback, issue closure, milestone closure, and terminal carrier closeout.

## Deferred Items

### Post-Merge Release Publication

- Locator: #1874 / main-push `loom-cli-release` workflow.
- Reason: release PR event must not publish artifacts.
- Activation condition: release PR merges to `main`.
- Does not currently block: pre-merge release PR validation.
- Statement: deferred is not completed.

### Final Issue And Milestone Closeout

- Locator: #1869/#1874, milestone #24.
- Reason: closure requires post-merge release readback and terminal carrier closeout.
- Activation condition: `loom release readback --version v0.26.1` returns published and carrier closeout-sync completes.
- Does not currently block: release PR review and merge.
- Statement: deferred is not completed.

## Phases

### Phase 1

- Objective: prepare release metadata and evidence.
- Deliverable: version bump, plugin payload metadata/hash, release readiness doc, WI-1874 carriers.
- Exit condition: package/release/suite validations pass locally.

### Phase 2

- Objective: merge release PR safely.
- Deliverable: PR metadata, review, local PR gate, hosted checks, controlled merge.
- Exit condition: release PR merges to `main`.

### Phase 3

- Objective: publish/read back/close out.
- Deliverable: `v0.26.1` tag, GitHub Release, npm package, workflow readback, terminal carrier closeout, issue/milestone closure.
- Exit condition: all release evidence and GitHub issue/milestone readbacks agree.

## Constraints

- Do not bump plugin surface version, host adapter version, skills registry version, or skill contract versions.
- Do not publish from the PR event.
- Do not overwrite an existing tag, npm version, or GitHub Release.
- Do not close #1869, #1874, or milestone #24 before release readback passes.
- Do not bypass review, PR gate, hosted checks, release readback, or closeout evidence.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/stamp_plugin_payload_metadata.py tools/version_surface_check.py`
  - `python3 tools/version_surface_check.py`
  - `python3 tools/check_release_surface.py`
  - `python3 tools/check_npm_package.py`
  - `python3 tools/check_cli_contract.py --surface release-readback`
  - `python3 tools/check_cli_contract.py --surface aggregate`
  - `npm pack --dry-run --json --ignore-scripts`
  - suite validate/evidence/carrier, fact-chain, shadow parity, PR metadata readback, PR gate, hosted checks
- Runtime evidence:
  - post-merge `loom release readback --target . --version v0.26.1 --release-judgment release_required --json`
- Behavior evidence:
  - `docs/evidence/v0.26.1-release-readiness.md`
- Scenario validation mapping:
  - S1 -> automated validation strategy: version/package/plugin metadata checks.
  - S2 -> automated validation strategy: release/package/suite/PR gate/hosted checks.
  - S3 -> automated validation strategy: post-merge release readback and closeout sync.
- Fresh verification evidence:
  - `.loom/progress/WI-1874.md`
- Execution ledger plan locator:
  - `.loom/specs/WI-1874/plan.md`
- Execution ledger validation evidence locator:
  - `.loom/specs/WI-1874/evidence-map.md`; `docs/evidence/v0.26.1-release-readiness.md`

## Test Strategy

- TDD or test-first expectation: release metadata bump only; preserve existing release/package contract checks.
- Regression coverage to add or preserve: preserve release-readback, aggregate CLI, package, and release surface contracts.
- Cases that are intentionally not automated: final GitHub/npm publication before merge.
- Acceptance test mapping:
  - A1 -> test evidence: version surface and package checks.
  - A2 -> test evidence: release readiness evidence review.
  - A3 -> test evidence: local and hosted pre-merge gates.
  - A4 -> test evidence: post-merge release readback.
  - A5 -> test evidence: closeout-sync and GitHub issue/milestone readback.

## Dependencies

- Blocking inputs:
  - #1869 implementation PR #1875 merged to `main`.
- Required coordination:
  - GitHub Release/npm publish workflow credentials must be available after merge.
- Rollback boundary:
  - Before merge, revert release metadata branch.
  - After merge, use release repair/readback path without overwriting published artifacts.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly non-applicable with rationale
- [x] Story business semantics are confirmed or explicitly non-applicable with rationale
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or non-applicability evidence
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has a non-applicability rationale and recheck condition
- [x] Risks and dependencies are explicit
