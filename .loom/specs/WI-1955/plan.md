# WI-1955 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1955 is a patch release and milestone closeout convergence item with frozen implementation scope from merged PR #1967 and is reviewable through spec, plan, implementation contract, evidence map, release readiness evidence, package validation, and release readback; consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, release readback, issue closeout, Phase closeout, and milestone closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if this work expands into new runtime behavior, release workflow mutation, credentials handling, #1933/#1935/v0.28.0 scope, or a second release track.
- Consumes:
  - Spec locator: `.loom/specs/WI-1955/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: no separate story readiness artifact is required because release scope is governed by #1954/#1955 and the merged #1928/#1930 implementation batch; plan validation, review, PR gate, release readback, and final closeout consume the spec rationale without treating a separate story artifact as completed; require story readiness if release scope expands.
  - Story Business Confirmation consumed state: no separate business confirmation artifact is required because the milestone issue tree is the accepted patch scope; plan validation, review, release readback, and final closeout consume the spec rationale without treating a separate business confirmation artifact as completed; require business confirmation if release scope changes beyond #1955.
- Produces:
  - Validation strategy by scenario: version/package checks, release checks, hosted checks, release readback.
  - Test strategy by acceptance: release/package CLI checks plus post-merge readback.
  - Fresh verification evidence expectation: `.loom/progress/WI-1955.md` latest validation summary and release readiness document.
- Locator:
  - Plan locator: `.loom/specs/WI-1955/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: `.loom/specs/WI-1955/spec.md`, #1955, #1967.
  - Freshness rule: refresh after version, package, plugin metadata, release readiness, review, PR metadata, hosted checks, or release readback changes.

## Implementation Goal

Deliver the `v0.27.1` release candidate and prepare it for release workflow publication after merge.

Explicitly deferred until after merge: GitHub tag, GitHub Release, npm publish, release readback, issue/Phase/milestone closure, and terminal carrier closeout.

## Deferred Items

### Post-Merge Release Publication

- Locator: #1955 / main-push `loom-cli-release` workflow.
- Reason: release PR event must not publish artifacts.
- Activation condition: release PR merges to `main`.
- Does not currently block: pre-merge release PR validation.
- Statement: deferred is not completed.

### Final Issue And Milestone Closeout

- Locator: #1928 / #1930 / #1955 / #1954 / milestone #26.
- Reason: closure requires post-merge release readback and terminal carrier closeout.
- Activation condition: `loom release readback --version v0.27.1` returns published and carrier closeout-sync completes.
- Does not currently block: release PR review and merge.
- Statement: deferred is not completed.

## Phases

### Phase 1

- Objective: prepare release metadata and evidence.
- Deliverable: version bump, plugin payload metadata/hash, release readiness doc, WI-1955 carriers.
- Exit condition: package/release/suite validations pass locally.

### Phase 2

- Objective: merge release PR safely.
- Deliverable: PR metadata, review, local PR gate, hosted checks, controlled merge.
- Exit condition: release PR merges to `main`.

### Phase 3

- Objective: publish/read back/close out.
- Deliverable: `v0.27.1` tag, GitHub Release, npm package, workflow readback, terminal carrier closeout, issue/Phase/milestone closure.
- Exit condition: all release evidence and GitHub issue/milestone readbacks agree.

## Constraints

- Do not bump plugin surface version, host adapter version, skills registry version, or skill contract versions.
- Do not publish from the PR event.
- Do not overwrite an existing tag, npm version, or GitHub Release.
- Do not close #1928, #1930, #1955, #1954, or milestone #26 before release readback passes.
- Do not add #1933 temporary hardcoding, #1935/v0.28.0 host adoption tax, or downstream repo-local `tools/loom.py` requirements.
- Do not bypass review, PR gate, hosted checks, release readback, or closeout evidence.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/check_release_surface.py tools/stamp_plugin_payload_metadata.py tools/version_surface_check.py`
  - `git diff --check`
  - `python3 tools/version_surface_check.py`
  - `python3 tools/check_release_surface.py`
  - `python3 tools/check_npm_package.py`
  - `npm pack --dry-run --json --ignore-scripts`
  - `python3 tools/loom.py skills release-check --target . --json`
  - `python3 tools/loom.py release readback --version v0.27.1 --release-judgment release_required --json`
  - suite validate/evidence/carrier, fact-chain, shadow parity, PR metadata readback, PR gate, hosted checks
- Manual checks: confirm #1928/#1930 implementation PR #1967 merged and #1955 remains open before release merge.
- Runtime evidence: post-merge `loom release readback --target . --version v0.27.1 --release-judgment release_required --json`
- Behavior evidence:
  - `docs/evidence/v0.27.1-release-readiness.md`
- Story scenario to evidence mapping: release-only mapping consumes the issue tree as the governing release scope.
- Story readiness consumed: no separate story readiness artifact is required; #1954/#1955 and merged PR #1967 define release readiness for validation, review, PR gate, release readback, and final closeout; require story readiness if new product scope is added.
- Story business confirmation consumed: no separate business confirmation artifact is required; the milestone issue tree is the accepted patch scope for validation, review, release readback, and final closeout; require business confirmation if release scope changes.
- Scenario validation mapping:
  - S1 -> automated validation strategy: version/package/plugin metadata checks.
  - S2 -> automated validation strategy: release/package/suite/PR gate/hosted checks.
  - S3 -> automated validation strategy: post-merge release readback and closeout sync.
- Fresh verification evidence: `.loom/progress/WI-1955.md`
- Execution ledger plan locator: `.loom/specs/WI-1955/plan.md`
- Execution ledger validation evidence locator: `.loom/specs/WI-1955/evidence-map.md`; `docs/evidence/v0.27.1-release-readiness.md`

## Test Strategy

- TDD or test-first expectation: release metadata bump only; preserve existing release/package contract checks.
- Regression coverage to add or preserve: preserve release-readback, package, and release surface contracts; #1928/#1930 regressions were added and passed in implementation PR #1967.
- Cases that are intentionally not automated: final GitHub/npm publication before merge.
- How failing tests or equivalent checks will be introduced before implementation: pre-release readback must report v0.27.1 as missing/unoccupied before merge; any occupied or inconsistent release artifact blocks.
- How passing tests or equivalent checks will be captured as test evidence: progress validation summary, release readiness document, PR checks, and post-merge release readback.
- Acceptance test mapping:
  - A1 -> test evidence: version surface and package checks.
  - A2 -> test evidence: release readiness evidence review.
  - A3 -> test evidence: local and hosted pre-merge gates.
  - A4 -> test evidence: post-merge release readback.
  - A5 -> test evidence: closeout-sync and GitHub issue/milestone readback.

## Subagent Output Integration

- Owned outputs: none for this release bump; main thread owns shared release carriers and external state.
- Integration owner: codex-main.
- Required evidence from each subagent: none; no subagent output is integrated for this release bump.
- Review or reconciliation needed before merge-ready: release PR review plus PR gate and hosted checks.
- Handoff notes locator: no handoff artifact is needed while the main thread owns release carriers and publication remains unblocked; review, PR gate, release readback, and closeout consume progress/status carriers instead of a handoff note; write handoff notes if release publication blocks or ownership changes.

## Dependencies

- Blocking inputs:
  - Implementation PR #1967 merged to `main`.
  - #1928 and #1930 regression validation passed in the implementation batch.
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
