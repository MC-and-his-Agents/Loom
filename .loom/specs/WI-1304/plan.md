# WI-1304 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator: this minimal suite is directly represented by this spec and plan.
- Full-path artifacts not_applicable: artifacts: contracts.md, readiness-checklist.md, research.md, suite-index.md; rationale: WI-1304 is a narrow gate-consumption implementation and the minimal suite carries the required contract, plan, validation mapping, and boundaries; consumer boundary: suite validate, spec review, implementation review, PR gate, merge-ready, and closeout may treat only those four full-path artifacts as not required for WI-1304; recheck condition: require the full suite if #1304 expands into broader suite validation behavior, PR gate policy, release behavior, or cross-repo migration.
- Consumes:
  - Spec locator: .loom/specs/WI-1304/spec.md
  - Scenario ids / locators: S1, S2
  - Acceptance ids / locators: A1, A2, A3, A4, A5
  - Story Readiness consumed state: NA; internal unblocker.
  - Story Business Confirmation consumed state: NA.
- Produces:
  - Validation strategy by scenario: targeted governance-profile and bootstrap-regression checks.
  - Test strategy by acceptance: structural runtime checks and source-surface regression check.
  - Fresh verification evidence expectation: local commands plus hosted PR checks on the current head.
- Locator:
  - Plan locator: .loom/specs/WI-1304/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: #1304; .loom/specs/WI-1304/spec.md.
  - Freshness rule: re-run validation after any runtime copy, manifest, init-result, or WI-1304 carrier change.

## Implementation Goal

Deliver a narrow governance maturity fix: detect a docs-only suite decision and approved spec review record as the formal-spec-or-NA proof for maturity, while preserving existing full/minimal suite behavior.

Explicitly deferred: any changes to suite validate, PR gate, implementation review, hosted CI policy, A-D contract PR content, or closeout semantics.

## Deferred Items

None.

## Story Artifacts

- Locator: story readiness and business confirmation surfaces
- Rationale: #1304 is a technical unblocker raised by a concrete gate failure.
- Recheck condition: require story shaping if this work expands into user-visible workflow behavior.
- Consumers that should not require it: spec review, implementation review, merge-ready, closeout.

## Phases

### Phase 1

- Objective: update governance_surface carrier detection and maturity facts.
- Deliverable: shared source, source mirror, installed runtime copy, skill runtime copies, manifest and init-result hashes.
- Exit condition: governance-profile status reports strong for the PR-A docs-only target when read through the updated runtime.

### Phase 2

- Objective: verify no runtime provenance drift or self-adoption regression.
- Deliverable: fact-chain, shadow parity, carrier refresh, runtime verify, and bootstrap-regression evidence.
- Exit condition: local checks pass and PR hosted checks can consume the current head.

## Constraints

- Do not weaken review, suite validation, PR head binding, CI, fact-chain, or closeout gates.
- Do not put PR-A/B/C/D contract changes into this branch.
- Keep runtime copies synchronized with the shared source.

## Validation

- Automated checks:
  - `git diff --check`
  - `python3 tools/loom.py suite validate --target . --item WI-1304 --json`
  - `python3 .loom/bin/loom_init.py verify --target .`
  - `python3 .loom/bin/loom_flow.py fact-chain --target .`
  - `python3 .loom/bin/loom_flow.py shadow-parity --target .`
  - `python3 .loom/bin/loom_flow.py carrier refresh --target . --dry-run`
  - `python3 .loom/bin/loom_flow.py governance-profile status --target /Users/mc/dev/Loom-worktrees/1264-regression-surface-contract --host github`
  - `python3 tools/loom_check.py --profile source --source-surface bootstrap-regression .`
- Manual checks: confirm diff scope is limited to governance_surface runtime/source copies, bootstrap hashes, and WI-1304 carriers.
- Runtime evidence: runtime verify and carrier refresh output.
- Behavior evidence: PR-A target governance-profile status reports strong.
- Scenario validation mapping:
  - S1 -> automated: governance-profile status against PR-A target.
  - S2 -> structural: bootstrap-regression and carrier refresh preserve fail-closed runtime drift behavior.
- Fresh verification evidence: PR validation section and hosted checks on current head.
- Execution ledger plan locator: .loom/specs/WI-1304/plan.md
- Execution ledger validation evidence locator: PR #1304 validation section.

## Test Strategy

- TDD or test-first expectation: reproduce the PR-A governance-profile downgrade, then validate strong maturity after the change.
- Regression coverage to add or preserve: bootstrap-regression root-self-adoption.
- Cases that are intentionally not automated: synthetic invalid docs-only fixtures are deferred because #1304 is a narrow unblocker and suite validate already owns invalid rationale classification.
- How failing tests or equivalent checks will be introduced before implementation: observed PR-A target returned light maturity before the change.
- How passing tests or equivalent checks will be captured as test evidence: command outputs in PR validation and hosted checks.
- Acceptance test mapping:
  - A1 -> structural check: governance-profile status against PR-A target.
  - A2 -> structural check: runtime verify.
  - A3 -> structural check: carrier refresh and bootstrap-regression.
  - A4 -> manual evidence: diff review confirms no suite validate or PR gate relaxation.
  - A5 -> manual evidence: PR-A remains separate and will rebase after #1304.

## Subagent Output Integration

- Owned outputs: read-only subagent confirmed #1304 should be a narrow unblocker and identified governance_surface as the minimal runtime surface.
- Integration owner: main thread.
- Required evidence from each subagent: root cause, affected files, runtime copy requirement, targeted checks, PR-A scope recommendation.
- Review or reconciliation needed before merge-ready: main thread review record for WI-1304 current head.
- Handoff notes locator: NA.

## Dependencies

- Blocking inputs: #1304 issue.
- Required coordination: PR-A #1297 waits for #1304 to merge before final rebase/gate.
- Rollback boundary: revert #1304 PR; A-D remain unmerged and can continue to wait.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly NA
- [x] Story business semantics are confirmed or explicitly NA
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or NA
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has rationale and recheck condition
- [x] Risks and dependencies are explicit
