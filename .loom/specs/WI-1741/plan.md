# WI-1741 Plan

## Suite Contract

- Suite path consumed: full
- Suite index locator: .loom/specs/WI-1741/suite-index.md
- Spec locator: .loom/specs/WI-1741/spec.md
- Scenario ids / locators: .loom/specs/WI-1741/spec.md#key-scenarios
- Acceptance ids / locators: .loom/specs/WI-1741/spec.md#acceptance-criteria
- Story Readiness consumed state: not required.
- Story Business Confirmation consumed state: not required.
- Validation strategy by scenario: ship wrapper contract fixture plus docs/skills/package checks.
- Test strategy by acceptance: `tools/check_cli_contract.py --fixture-group ship-wrapper`.
- Fresh verification evidence expectation: local validation summary in .loom/progress/WI-1741.md and PR checks.
- Plan locator: .loom/specs/WI-1741/plan.md
- Source spec / issue / PR / doc locator: GitHub issue #1741.
- Freshness rule: stale after PR head, validation mapping, or ship docs contract changes.

## Implementation Goal

Deliver changed-path validation profile selection in `loom ship` without expanding the repair chain, closeout, or release scope.

## Deferred Items

- Locator: GitHub issues #1739, #1742, #1743.
- Reason: those lanes own repair chain, closeout e2e, and release respectively.
- Activation condition: #1741 PR merged and dependent lanes begin.
- Does not currently block: WI-1741 implementation and validation.
- Statement: deferred is not completed.

## Not Required Items

- Locator: release publish, full closeout PR execution, and metadata/carrier/shadow repair chain.
- Rationale: #1741 only selects and reports validation profile.
- Recheck condition: require those artifacts in #1739/#1742/#1743.
- Consumers that should not require it: WI-1741 review, merge-ready, and closeout.

## Phases

### Phase 1

- Objective: Add validation profile classifier and changed-path readback.
- Deliverable: `tools/loom.py`.
- Exit condition: selector returns light, standard, full, or release with reasons and commands.

### Phase 2

- Objective: Add regression contract coverage.
- Deliverable: `tools/check_cli_contract.py`.
- Exit condition: ship wrapper fixture covers docs/package tombstone, runtime full, release, explicit override, and PR files readback.

### Phase 3

- Objective: Align user-facing contract docs and Loom carriers.
- Deliverable: README, CLI matrix, WI-1741 suite/carriers.
- Exit condition: ship docs contract and suite validations pass.

## Constraints

- Architectural or governance constraints: validation profile is separate from governance intensity and closeout policy.
- Workspace / rollout constraints: branch `work/1741-validation-profile`, worktree `/Users/mc/dev/Loom-WI-1741-validation-profile`.
- Purity or scope constraints: no release publish, no repair chain implementation, no closeout e2e.

## Validation

- Automated checks: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`.
- Manual checks: inspect dry-run payload fields and docs snippets.
- Runtime evidence: .loom/progress/WI-1741.md.
- Behavior evidence: ship wrapper fixture and docs contract.
- Story scenario to evidence mapping: S1-S3 map to ship wrapper fixtures.
- Scenario validation mapping:
  - S1 -> automated.
  - S2 -> automated.
  - S3 -> automated.
- Fresh verification evidence: local validation plus hosted checks before merge.
- Execution ledger plan locator: .loom/specs/WI-1741/plan.md
- Execution ledger validation evidence locator: .loom/specs/WI-1741/evidence-map.md

## Test Strategy

- TDD or test-first expectation: selector behavior is covered by contract fixtures.
- Regression coverage to add or preserve: preserve existing ship wrapper dry-run/apply/inference contracts.
- Cases that are intentionally not automated: live GitHub PR files readback beyond fixture shape; hosted PR checks cover the real branch.
- How failing tests or equivalent checks will be introduced before implementation: fixture assertions fail if profile, source surface, or override behavior drifts.
- How passing tests or equivalent checks will be captured as test evidence: validation summary and PR checks.
- Acceptance test mapping:
  - A1 -> test evidence: `tools/check_cli_contract.py --fixture-group ship-wrapper`.
  - A2 -> test evidence: docs/package tombstone fixture in `tools/check_cli_contract.py`.
  - A3 -> test evidence: runtime/harness fixture in `tools/check_cli_contract.py`.
  - A4 -> test evidence: release profile fixture in `tools/check_cli_contract.py`.
  - A5 -> test evidence: explicit full override fixture in `tools/check_cli_contract.py`.

## Subagent Output Integration

- Owned outputs: #1741 initial inventory from Leibniz was read-only; no subagent writes were integrated.
- Integration owner: main controller.
- Required evidence from each subagent: summary only.
- Review or reconciliation needed before merge-ready: main controller validates branch, PR body, review, carrier, and checks.
- Handoff notes locator, or not-required rationale: not required.

## Dependencies

- Blocking inputs: #1735 and #1740 are already complete; #1741 consumes the short ship contract and review drift classification.
- Required coordination: #1739 must not consume unmerged #1741 behavior until this PR merges.
- Rollback boundary: revert the PR if profile selection under-validates or breaks ship wrapper contracts.

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
