# Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md; rationale: WI-1898 is a focused docs-only contract freeze with direct issue scope and no runtime implementation; consumer boundary: suite validate, review, PR gate, merge-ready, and closeout for WI-1898; recheck condition: require full suite artifacts if the work expands into runtime path resolver implementation, repository mutation, gate behavior, migration apply, or release behavior.
- Consumes:
  - Spec locator: .loom/specs/WI-1898/spec.md
  - Scenario ids / locators: S1-S3 in .loom/specs/WI-1898/spec.md#key-scenarios
  - Acceptance ids / locators: A1-A5 in .loom/specs/WI-1898/spec.md#acceptance-criteria
  - Story Readiness consumed state: not required; issue #1898 is the scoped readiness carrier.
  - Story Business Confirmation consumed state: not required; internal operating-layer contract.
- Produces:
  - Validation strategy by scenario: structural docs/readback checks.
  - Test strategy by acceptance: suite validation, evidence-map validation, carrier validation, diff hygiene, and targeted text/link checks.
  - Fresh verification evidence expectation: current branch/head validation summary in .loom/progress/WI-1898.md before review.
- Locator:
  - Plan locator: .loom/specs/WI-1898/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: issue #1898; docs/adoption/installation-taxonomy.md; docs/adoption/global-cli-user-plugin-contract.md; docs/adoption/host-adapter-matrix.md
  - Freshness rule: Recheck when linked contract files or FR #1897 scope changes.

## Implementation Goal

- Deliver a new authoritative docs contract for repo/global artifact classification.
- Update adoption/host docs to point to the new contract without duplicating the full rule set.
- Keep implementation, migration, release, and gate behavior deferred to later Work Items.

## Deferred Items

### Deferred Item 1

- Locator: #1899
- Reason: Runtime path resolver implementation depends on this contract.
- Activation condition: #1898 merged and closed.
- Does not currently block: contract freeze and docs validation.
- Statement: deferred is not completed.

### Deferred Item 2

- Locator: #1900 / #1901
- Reason: Repo carrier slimdown and gate independence validation require implementation after path resolver semantics exist.
- Activation condition: #1898 and relevant implementation slice are complete.
- Does not currently block: contract freeze.
- Statement: deferred is not completed.

## Deferred / Out Of Scope Items

### Runtime Migration Apply

- Locator: #1910
- Rationale: WI-1898 only freezes classification; legacy repo migration apply belongs to FR #1908.
- Recheck condition: Recheck when legacy migration implementation consumes this contract.
- Consumers that should not require it: review, merge-ready, and closeout for WI-1898.

## Phases

### Phase 1

- Objective: Add the authoritative repo/global artifact classification contract.
- Deliverable: docs/methodology/harness/repo-global-artifact-classification.md
- Exit condition: Contract defines authority rule, classification matrix, repo carrier shape, global path contract, consumer boundary, migration rule, and validation requirements.

### Phase 2

- Objective: Link adoption and host contracts to the new boundary.
- Deliverable: updates to installation taxonomy, global CLI/user plugin contract, host adapter matrix, and harness README.
- Exit condition: Linked docs do not redefine contradictory cache/adoption/plugin authority.

## Constraints

- Architectural or governance constraints: Repository truth must not move global; global cache must not satisfy review, merge-ready, closeout, or release truth.
- Workspace / rollout constraints: Docs-only change; no command behavior, workflow, or release mutation.
- Purity or scope constraints: Do not implement #1899, #1900, #1901, or #1908 behavior.

## Validation

- Automated checks:
  - `python3 tools/loom.py suite validate --target . --item WI-1898 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1898 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1898 --json`
  - `git diff --check`
- Manual checks:
  - Confirm linked adoption/host docs point to the new contract instead of duplicating the matrix.
- Runtime evidence: not required; no runtime behavior changes.
- Behavior evidence: contract text and cross-doc links.
- Story scenario to evidence mapping:
  - S1 -> classification matrix.
  - S2 -> repo carrier shape and global path contract.
  - S3 -> consumer boundary and validation requirements.
- Story readiness consumed: not required; issue #1898 is scoped.
- Story business confirmation locator or not-required rationale: not required; internal operating-layer contract.
- Scenario validation mapping:
  - S1 -> structural docs evidence.
  - S2 -> structural docs evidence.
  - S3 -> structural docs evidence.
- Fresh verification evidence: .loom/progress/WI-1898.md validation summary.
- Execution ledger plan locator: .loom/specs/WI-1898/plan.md
- Execution ledger validation evidence locator: .loom/specs/WI-1898/evidence-map.md

## Test Strategy

- TDD or test-first expectation: Structural docs validation is sufficient for this docs-only contract; no runtime tests are introduced.
- Regression coverage to add or preserve: Suite evidence/carrier validation and diff hygiene.
- Cases that are intentionally not automated: Human semantic review of whether the classification boundary is coherent.
- How failing tests or equivalent checks will be introduced before implementation: Suite templates initially fail until evidence-map/task-carrier rows and validation summary are authored.
- How passing tests or equivalent checks will be captured as test evidence: Validation commands are recorded in progress and review artifacts.
- Acceptance test mapping:
  - A1 -> structural check / evidence-map EV-001.
  - A2 -> structural check / evidence-map EV-002.
  - A3 -> structural check / evidence-map EV-003.
  - A4 -> structural check / evidence-map EV-004.
  - A5 -> test evidence / suite validation / evidence-map EV-005.
- How User Story acceptance scenarios map to tests, checks, manual validation, or not-required evidence:
  - Story path is not required for this scoped internal contract Work Item.

## Subagent Output Integration

- Owned outputs: not required; main thread owns the docs-only edit.
- Integration owner: codex-main-thread.
- Required evidence from each subagent: not required.
- Review or reconciliation needed before merge-ready: authored review record and standard gate chain.
- Handoff notes locator, or not-required: not required.

## Dependencies

- Blocking inputs: none.
- Required coordination: FR #1897 consumes this contract before #1899/#1900/#1901.
- Rollback boundary: revert WI-1898 docs and carrier files only.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly not required
- [x] Story business semantics are confirmed or explicitly not required
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or a not-required rationale
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has a not-required rationale and recheck condition
- [x] Risks and dependencies are explicit
