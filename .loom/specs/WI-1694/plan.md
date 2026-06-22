# WI-1694 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1694`
- Consumes:
  - Spec locator: `.loom/specs/WI-1694/spec.md`
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: N/A
  - Story Business Confirmation consumed state: N/A
- Produces:
  - Validation strategy by scenario: targeted docs / skills / fixture checks.
  - Test strategy by acceptance: static diff review plus CLI contract fixtures.
  - Fresh verification evidence expectation: `.loom/progress/WI-1694.md`
- Locator:
  - Plan locator: `.loom/specs/WI-1694/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: issue #1694 and `.loom/specs/WI-1694/spec.md`
  - Freshness rule: Re-run validation after generated skills or fixture edits.

## Implementation Goal

- Add a README daily delivery path that makes `loom ship` the ordinary user-facing command after install/adoption.
- Update source skills so `loom-init`, `loom-merge-ready`, and `loom-retire` point to `loom ship` for ordinary delivery while preserving advanced diagnostics.
- Add a targeted fixture assertion so the entry contract does not drift.
- Defer release and milestone closeout to #1696.

## Deferred Items

- Release closeout
  - Locator: #1696
  - Reason: release / milestone closeout is a separate Work Item.
  - Activation condition: #1694 PR merged and parent issue closeout is ready.
  - Does not currently block: README / skills / fixture convergence.
  - Statement: deferred is not completed.

## Excluded Items

- Runtime behavior changes to `tools/loom.py` or `skills/shared/scripts/loom_flow.py`.
- Release publishing and milestone closeout.
- New skill surface or new closeout policy vocabulary.

## Phases

### Phase 1

- Objective: Update user-facing README delivery path.
- Deliverable: README and README.zh-CN daily delivery sections.
- Exit condition: English and Chinese README both describe `loom ship` and the closeout PR upgrade boundary.

### Phase 2

- Objective: Align skills source and generated mirrors.
- Deliverable: `src/skills` updates plus generated `skills/` and plugin mirrors.
- Exit condition: `tools/skills_surface.py check` passes.

### Phase 3

- Objective: Guard the entry contract.
- Deliverable: `ship-wrapper` docs / skills drift assertions.
- Exit condition: `tools/check_cli_contract.py --fixture-group ship-wrapper` passes.

## Constraints

- Architectural or governance constraints: do not redefine closeout policy outside the existing closeout gate contract.
- Workspace / rollout constraints: implement only in `/Users/mc/dev/Loom-WI-1694`.
- Purity or scope constraints: no release, parent, milestone, or runtime closeout changes in this PR.

## Validation

- Automated checks:
  - `git diff --check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group merge-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1694 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1694`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1694`
- Manual checks: inspect English / Chinese README parity and confirm Chinese additions avoid unnecessary English outside command names and stable terms.
- Runtime evidence: `.loom/progress/WI-1694.md`
- Behavior evidence: README / skills source / generated mirrors / fixture diff.
- Story scenario to evidence mapping: N/A; scenarios are in `spec.md`.
- Story readiness consumed: N/A.
- Story business confirmation locator or N/A rationale: N/A.
- Scenario validation mapping:
  - S1 -> automated
  - S2 -> automated
  - S3 -> automated
- Fresh verification evidence: `.loom/progress/WI-1694.md`
- Execution ledger plan locator: `.loom/specs/WI-1694/plan.md`
- Execution ledger validation evidence locator: `.loom/progress/WI-1694.md`

## Test Strategy

- TDD or test-first expectation: preserve existing ship / merge wrapper fixtures and add a narrow drift guard.
- Regression coverage to add or preserve: `ship-wrapper` now covers docs / skills entry contract and source/generated mirror drift.
- Cases that are intentionally not automated: full prose quality is manually reviewed in README diff.
- How failing tests or equivalent checks will be introduced before implementation: the new fixture fails if required `loom ship` entry snippets are absent.
- How passing tests or equivalent checks will be captured as test evidence: commands listed in Validation.
- Acceptance test mapping:
  - A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`
  - A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`
  - A3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`
  - A4 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
  - A5 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`

## Subagent Output Integration

- Owned outputs: read-only inventory from Goodall.
- Integration owner: main agent.
- Required evidence from each subagent: summary of relevant files, validation commands, and risks.
- Review or reconciliation needed before merge-ready: main agent reviews diff and reruns targeted checks.
- Handoff notes locator, or N/A: N/A.

## Dependencies

- Blocking inputs: none after #1691/#1692/#1695 landed on main.
- Required coordination: #1696 release closeout remains separate.
- Rollback boundary: README / skills / fixture diff only.

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
