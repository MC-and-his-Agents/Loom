# Plan

## Suite Contract

- Suite path consumed: full
- Suite index locator, or `not required` rationale: .loom/specs/WI-1235/suite-index.md
- Consumes:
  - Spec locator: .loom/specs/WI-1235/spec.md
  - Scenario ids / locators: S1-S3 in spec.md
  - Acceptance ids / locators: A1-A5 in spec.md
  - Story Readiness consumed state: not required
  - Story Business Confirmation consumed state: not required
- Produces:
  - Validation strategy by scenario: focused governance-closeout contract plus aggregate CLI contract.
  - Test strategy by acceptance: targeted fixture coverage in `tools/check_cli_contract.py`.
  - Fresh verification evidence expectation: py_compile, governance-closeout, aggregate, suite validate/evidence/carrier validate, fact-chain, PR checks/readback.
- Locator:
  - Plan locator: .loom/specs/WI-1235/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: GitHub issue #1235; .loom/specs/WI-1235/spec.md.
  - Freshness rule: Recheck after repair CLI, generated runtime, test fixture, PR head, review, or gate input changes.

## Implementation Goal

- Deliver `repair plan/apply` as a safe carrier closeout path for host-complete active carriers.
- Explicitly defer #1236, #1237, #1296, parent FR closeout, release/tag/npm, and issue/project mutation.

## Deferred Items

- Locator: GitHub issues #1236, #1237, #1296
- Reason: dependency order; they consume #1235 stable behavior after merge.
- Activation condition: #1235 is merged and issue #1235 is closed/completed.
- Does not currently block: #1235 PR validation.
- Statement: deferred is not completed.

## Excluded Items

- Locator: release/tag/npm publish
- Rationale: #1235 is source/runtime behavior only; #1296 owns release/no-release closeout.
- Recheck condition: before #1296.
- Consumers that should not require it: #1235 review/merge-ready.

## Phases

### Phase 1

- Objective: Add shared runtime carrier repair plan/apply behavior.
- Deliverable: `src/skills/shared/scripts/loom_flow.py` and generated runtime copies support repair plan/apply with host truth readback and repo-local carrier write set.
- Exit condition: plan/dry-run/apply fixture covers terminal metadata, idle status, idle init-result, fact-chain idle readback, and no host mutations.

### Phase 2

- Objective: Integrate public root CLI and fail-closed action composition.
- Deliverable: `tools/loom.py` exposes `repair plan/apply`, blocks mixed installed-surface/carrier apply, and updates public command summary.
- Exit condition: root CLI JSON behavior matches safe carrier repair semantics.

### Phase 3

- Objective: Add regression evidence and synchronize skills payloads.
- Deliverable: `tools/check_cli_contract.py` coverage for happy path, dry-run, invalid output, omitted issue, ambiguous retained item, multi-issue locator, mixed action block, and aggregate generated-tree drift.
- Exit condition: py_compile, governance-closeout, and aggregate checks pass.

## Constraints

- Architectural or governance constraints: no host mutations; no schema/failure vocabulary changes beyond #1235 repair ownership semantics; generated runtime copies must match source.
- Workspace / rollout constraints: formal worktree `/Users/mc/dev/Loom-worktrees/1235-safe-repair-sync`, branch `work/1235-safe-repair-sync`.
- Purity or scope constraints: do not touch Round 10/11/deferred, #1236/#1237/#1296 implementation, release/tag/npm, or unrelated refactors.

## Validation

- Automated checks:
  - `python3 -m py_compile tools/loom.py tools/check_cli_contract.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py`
  - `python3 tools/check_cli_contract.py --surface governance-closeout`
  - `python3 tools/check_cli_contract.py --surface aggregate`
  - `python3 tools/loom.py suite validate --target . --item WI-1235 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1235 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1235 --json`
  - `python3 tools/loom.py fact-chain --target . --json`
- Manual checks: review PR body machine carrier, issue/PR/head alignment, no host mutation actions in repair outputs.
- Runtime evidence: generated skill runtime copies refreshed by `python3 tools/loom.py skills generate --apply --json`.
- Behavior evidence: `assert_repair_apply_carrier_closeout_contract`.
- Story scenario to evidence mapping: S1-S3 -> governance-closeout contract.
- Story readiness consumed: not required.
- Story business confirmation locator or `not required` rationale: not required.
- Scenario validation mapping:
  - S1 -> automated: governance-closeout repair plan fixture.
  - S2 -> automated: governance-closeout dry-run/apply/fact-chain fixture.
  - S3 -> automated: governance-closeout fail-closed fixtures.
- Fresh verification evidence: evidence-map rows EV-001 through EV-004.
- Execution ledger plan locator: .loom/specs/WI-1235/plan.md
- Execution ledger validation evidence locator: .loom/specs/WI-1235/evidence-map.md

## Test Strategy

- TDD or test-first expectation: regression fixtures were added before final aggregate validation.
- Regression coverage to add or preserve: happy path, dry-run non-mutation, explicit apply write set, omitted issue selector, ambiguous retained item, multi-issue locator, invalid output, mixed installed-surface action, generated-tree drift.
- Cases that are intentionally not automated: live GitHub issue/project mutation by repair commands is not automated because it is forbidden; release/tag/npm verification belongs to #1296.
- How failing tests or equivalent checks will be introduced before implementation: targeted fixture assertions in `tools/check_cli_contract.py`.
- How passing tests or equivalent checks will be captured as test evidence: command results recorded in .loom/progress/WI-1235.md and .loom/specs/WI-1235/evidence-map.md.
- Acceptance test mapping:
  - A1 -> test evidence: governance-closeout explicit apply fixture.
  - A2 -> test evidence: plan and dry-run non-mutation assertions.
  - A3 -> test evidence: omitted issue, ambiguous retained item, multi-issue locator, invalid output, mixed action block assertions.
  - A4 -> test evidence: governance-closeout and aggregate command pass.
  - A5 -> manual/host evidence pending: PR, checks, merge, issue closeout readback.

## Subagent Output Integration

- Owned outputs: read-only review findings for issue selector, mixed action pass semantics, write preflight, CLI metadata, and missing drift tests.
- Integration owner: main Codex agent.
- Required evidence from each subagent: findings with file/line references and no code writes.
- Review or reconciliation needed before merge-ready: main agent applied fixes and reran targeted/aggregate validation.
- Handoff notes locator, or `not required`: current Codex thread.

## Dependencies

- Blocking inputs: #1232, #1233, #1234 closed/completed; #1235 issue acceptance criteria.
- Required coordination: #1236/#1237 must wait for #1235 merge before final implementation consumption.
- Rollback boundary: revert #1235 commit/PR; no host state is mutated by repair command.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly `not required`
- [x] Story business semantics are confirmed or explicitly `not required`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not required`
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has `not required` rationale and recheck condition
- [x] Risks and dependencies are explicit
