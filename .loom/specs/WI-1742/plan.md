# WI-1742 Plan

## Suite Contract

- Suite path consumed: full
- Suite index locator: .loom/specs/WI-1742/suite-index.md
- Consumes:
  - Spec locator: .loom/specs/WI-1742/spec.md
  - Scenario ids / locators: .loom/specs/WI-1742/spec.md#key-scenarios
  - Acceptance ids / locators: .loom/specs/WI-1742/spec.md#acceptance-criteria
  - Story Readiness consumed state: not required.
  - Story Business Confirmation consumed state: not required.
- Produces:
  - Validation strategy by scenario: ship-wrapper fixture group.
  - Test strategy by acceptance: targeted CLI contract checks plus suite/carrier validation.
  - Fresh verification evidence expectation: local validation summary in .loom/progress/WI-1742.md and PR checks.
- Locator:
  - Plan locator: .loom/specs/WI-1742/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1742/spec.md and issue #1742.
  - Freshness rule: re-run validation after every branch head change.

## Implementation Goal

Deliver a focused regression fixture that proves ordinary light/standard `loom ship --apply` consumes inline / host-only closeout facts, while release and versioned terminal carrier inputs still require an explicit closeout path.

No release publish, permission behavior, or #1743 release closeout is delivered by this Work Item.

## Deferred Items

No deferred items.

## Not Required Items

| Subject | Rationale | Recheck condition | Consumers that should not require it |
| --- | --- | --- | --- |
| Real release publish | #1743 owns v0.20.0 release. | Starting #1743. | WI-1742 review and merge-ready |
| GitHub permission model change | #1742 only adds deterministic fixture coverage. | A future issue changes host permissions. | WI-1742 review and merge-ready |

## Phases

### Phase 1

- Objective: Add deterministic ship-wrapper fixture coverage.
- Deliverable: `assert_ship_inline_host_only_closeout_e2e_contract` in `tools/check_cli_contract.py`.
- Exit condition: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper` passes.

### Phase 2

- Objective: Refresh WI-1742 carriers and review evidence.
- Deliverable: suite files, task carrier, recovery/status, review record, carrier refresh, shadow parity.
- Exit condition: suite validate, suite evidence validate, suite carrier validate, carrier refresh, and shadow parity pass.

## Constraints

- Architectural or governance constraints: keep implementation inside ship-wrapper fixture coverage; do not change release publication.
- Workspace / rollout constraints: branch `work/1742-closeout-e2e`; worktree `/Users/mc/dev/Loom-WI-1742-closeout-e2e`.
- Purity or scope constraints: no writes in `/Users/mc/dev/Loom`; no changes to #1711-#1722 or v0.19.0 release state.

## Validation

- Automated checks:
  - `git diff --check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1742 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1742 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1742 --json`
- Manual checks: readback PR metadata, issue state, checks, and merge commit before closeout.
- Runtime evidence: .loom/progress/WI-1742.md.
- Behavior evidence: `tools/check_cli_contract.py` ship-wrapper fixture.
- Scenario validation mapping:
  - S1 -> automated ship-wrapper fixture.
  - S2 -> automated ship-wrapper fixture.
  - S3 -> automated ship-wrapper fixture.
- Fresh verification evidence: update `.loom/progress/WI-1742.md` after validation.
- Execution ledger plan locator: .loom/specs/WI-1742/plan.md
- Execution ledger validation evidence locator: .loom/specs/WI-1742/evidence-map.md

## Test Strategy

- TDD or test-first expectation: fixture assertions define the regression boundary before PR merge.
- Regression coverage to add or preserve: light host-only closeout, standard host-only closeout, release blocker, versioned terminal blocker.
- Cases that are intentionally not automated: real GitHub Release and npm publish, both owned by #1743.
- How failing tests or equivalent checks will be introduced before implementation: the new fixture would fail if ship stops consuming host closeout readback or creates a closeout PR for ordinary cases.
- How passing tests or equivalent checks will be captured as test evidence: validation summary in `.loom/progress/WI-1742.md`.
- Acceptance test mapping:
  - A1 -> test evidence: ship-wrapper fixture light case in `tools/check_cli_contract.py`.
  - A2 -> test evidence: ship-wrapper fixture standard case in `tools/check_cli_contract.py`.
  - A3 -> test evidence: ship-wrapper fixture closeout readback assertions in `tools/check_cli_contract.py`.
  - A4 -> test evidence: ship-wrapper fixture release and versioned terminal blockers in `tools/check_cli_contract.py`.
  - A5 -> test evidence: suite evidence and carrier validation.

## Subagent Output Integration

- Owned outputs: one read-only explorer inspected fixture gaps; no delegated writes.
- Integration owner: main controller.
- Required evidence from each subagent: summary only; implementation remains in this worktree.
- Review or reconciliation needed before merge-ready: main controller review record and PR gate.
- Handoff notes locator, or not-required rationale: not required.

## Dependencies

- Blocking inputs: #1737, #1739, and #1741 are closed.
- Required coordination: #1743 remains pending until #1742 closes.
- Rollback boundary: revert this PR only; it does not alter release state.

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
