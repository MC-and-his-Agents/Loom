# WI-1691 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1691`
- Consumes:
  - Spec locator: `.loom/specs/WI-1691/spec.md`
  - Scenario ids / locators: S1-S4
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: N/A
  - Story Business Confirmation consumed state: N/A
- Produces:
  - Validation strategy by scenario: focused root CLI wrapper contract tests and implementation review.
  - Test strategy by acceptance: `ship-wrapper` surface plus adjacent merge/closeout wrapper surfaces.
  - Fresh verification evidence expectation: `.loom/specs/WI-1691/evidence-map.md`
- Locator:
  - Plan locator: `.loom/specs/WI-1691/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: issue #1691 and `.loom/specs/WI-1691/spec.md`
  - Freshness rule: Re-run focused checks after CLI wrapper, delegated args, closeout policy, or carrier changes.

## Implementation Goal

- Deliver `loom ship --apply` as the first productized merge-and-host-closeout path.
- Keep repo carrier closeout PR creation out of the default path unless policy requires explicit escalation.

## Deferred Items

- `controlled-merge --closeout-run`
  - Locator: #1692
  - Reason: controlled-merge native closeout-run flag is a separate consumer of the same closeout policy.
  - Activation condition: #1691 apply wrapper is merged.
  - Does not currently block: #1691 root `ship --apply` wrapper.
  - Statement: deferred is not completed.

## Excluded Items

- README/skills/fixture convergence: owned by #1694.
- milestone release: owned by #1696.
- versioned carrier batching: governed by closeout policy and later explicit closeout queue paths.

## Phases

### Phase 1

- Objective: Add apply-path orchestration to root `loom ship`.
- Deliverable: `tools/loom.py` can run safe metadata repair, gates, controlled merge execute, host reconciliation sync, and final closeout check.
- Exit condition: focused wrapper contract pass path succeeds.

### Phase 2

- Objective: Add blocker and escalation guards.
- Deliverable: `tools/check_cli_contract.py --surface ship-wrapper` proves gate blockers stop before merge, and implementation code fails closed for non-default closeout policies.
- Exit condition: adjacent merge/closeout wrapper surfaces remain stable.

## Constraints

- Architectural or governance constraints: reuse existing root wrapper delegation and runtime payload helpers; do not add a new orchestration framework for #1691.
- Workspace / rollout constraints: work stays on branch `work/1691-ship-apply` in `/Users/mc/dev/Loom-WI-1691`.
- Purity or scope constraints: no default closeout PR creation, release publishing, controlled-merge runtime closeout-run flag, or versioned carrier closeout from `ship --apply`.

## Validation

- Automated checks:
  - `git diff --check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper --surface closeout-wrapper --surface ship-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1691 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1691`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1691`
  - `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1691 --build-evidence .loom/progress/WI-1691-build-evidence.json`
- Manual checks: inspect diff for scope containment and non-default closeout PR guard.
- Runtime evidence: `ship-wrapper` contract invokes `handle_ship` with mocked delegated payloads.
- Behavior evidence: `tools/loom.py` `handle_ship`, closeout policy admission, controlled merge apply delegation, and host closeout delegation.
- Story scenario to evidence mapping: N/A; scenarios are in `spec.md`.
- Story readiness consumed: N/A.
- Story business confirmation locator or N/A rationale: N/A; no product-domain business semantics change.
- Scenario validation mapping:
  - S1 -> automated
  - S2 -> automated
  - S3 -> structural implementation review of closeout policy admission in `tools/loom.py`
  - S4 -> structural implementation review of target-branch admission in `tools/loom.py`
- Fresh verification evidence: `.loom/specs/WI-1691/evidence-map.md`
- Execution ledger plan locator: `.loom/specs/WI-1691/plan.md`
- Execution ledger validation evidence locator: `.loom/specs/WI-1691/evidence-map.md`

## Test Strategy

- TDD or test-first expectation: add the wrapper contract regression while adding the apply handler.
- Regression coverage to add or preserve: dry-run sequence, apply sequence, controlled merge execute flag, host reconciliation apply flag, final closeout check, closeout PR default false, and gate blocker no-merge behavior.
- Cases that are intentionally not automated: live GitHub status variations are covered by delegated PR gate, controlled merge, reconciliation, and closeout surfaces.
- How failing tests or equivalent checks will be introduced before implementation: the existing `ship --apply` fail-closed assertion is replaced by apply-path contract tests.
- How passing tests or equivalent checks will be captured as test evidence: commands listed in Validation and evidence map rows.
- Acceptance test mapping:
  - A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
  - A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
  - A3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
  - A4 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
  - A5 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`

## Subagent Output Integration

- Owned outputs: read-only test contract orientation from Plato subagent.
- Integration owner: main agent.
- Required evidence from each subagent: summary consumed into this plan and wrapper test focus; no subagent-authored files.
- Review or reconciliation needed before merge-ready: standard spec review, implementation review, PR gate, merge-ready, and closeout.
- Handoff notes locator, or N/A: N/A.

## Dependencies

- Blocking inputs: #1690 and #1695 are complete; #1683/#1687 prerequisites are complete.
- Required coordination: #1692 consumes this apply path for controlled-merge closeout-run integration; #1694 consumes the final user-facing ship path.
- Rollback boundary: revert `tools/loom.py`, `tools/check_cli_contract.py`, and WI-1691 carriers for this PR.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly N/A
- [x] Story business semantics are confirmed or explicitly N/A
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or N/A
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has N/A rationale and recheck condition
- [x] Risks and dependencies are explicit
