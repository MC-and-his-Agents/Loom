# Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator: `.loom/specs/WI-1692/`
- Full-suite-artifacts not_applicable: rationale: WI-1692 uses minimal planning because the implementation is constrained to `tools/loom.py`, focused wrapper tests, and WI-1692 carriers; consumer boundary: build, review, merge-ready, PR gate, hosted CI, controlled merge, and closeout consume this plan plus current-head review and PR metadata; recheck condition: require full suite artifacts if the change expands into runtime `loom_flow.py`, release/version behavior, external host permissions, destructive writes, or broad documentation/skill convergence.
- Consumes:
  - Spec locator: `.loom/specs/WI-1692/spec.md`
  - Scenario ids / locators: S1, S2, S3, S4 in the spec.
  - Acceptance ids / locators: A1 through A5 in the spec.
  - Story Readiness consumed state: no separate story readiness artifact is required for this internal CLI governance Work Item.
  - Story Business Confirmation consumed state: no business-domain behavior is changed.
- Produces:
  - Validation strategy by scenario: focused wrapper contract tests plus adjacent wrapper surfaces.
  - Test strategy by acceptance: `tools/check_cli_contract.py --fixture-group merge-wrapper`.
  - Fresh verification evidence expectation: local command output and PR #1707 hosted checks.
- Locator:
  - Plan locator: `.loom/specs/WI-1692/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: `.loom/specs/WI-1692/spec.md`, issue #1692, issue #1695, PR #1707.
  - Freshness rule: rerun after code, carrier, review, or PR metadata changes.

## Implementation Goal

- Deliver an explicit `--closeout-run` transition on `loom merge run --apply`.
- Keep default merge wrapper behavior unchanged.
- Make closeout mode policy explicit:
  - `inline`: call existing closeout-run payload helper.
  - `host_only`: perform host reconciliation and closeout readback only.
  - `batched_carrier_pr` / `full_closeout_pr`: fail closed before merge.

## Deferred Items

### Deferred Item 1

- Locator: #1694
- Reason: README, skills, and fixtures should converge on `loom ship` after #1692 is available.
- Activation condition: #1692 PR merged.
- Does not currently block: implementation of the advanced `merge --closeout-run` transition.
- Statement: deferred is not completed.

## Nonrequired Items

### Nonrequired Item 1

- Locator: Story Readiness and Story Business Confirmation.
- Rationale: this is an internal CLI governance transition under an already-scoped milestone.
- Recheck condition: if the change becomes user-facing documentation or public onboarding behavior.
- Consumer boundary: review, merge-ready, and closeout for PR #1707 should not require separate story artifacts.

## Phases

### Phase 1

- Objective: Add opt-in wrapper arguments and preserve default behavior.
- Deliverable: `tools/loom.py` parser and compatibility path.
- Exit condition: existing merge wrapper contract still passes.

### Phase 2

- Objective: Implement policy-aware closeout behavior.
- Deliverable: inline, host-only, and fail-closed upgraded mode paths.
- Exit condition: focused `merge-wrapper` regression tests pass.

### Phase 3

- Objective: Refresh carriers and review evidence for PR gate consumption.
- Deliverable: WI-1692 work item, minimal suite, progress, review, and PR metadata.
- Exit condition: local fact-chain, state-check, PR gate, and hosted checks consume WI-1692.

## Constraints

- Architectural or governance constraints:
  - Do not replace `loom ship` as the main delivery entry.
  - Do not push closeout orchestration into runtime `controlled-merge`.
  - Do not create closeout PRs from this path.
- Workspace / rollout constraints:
  - Work only in `/Users/mc/dev/Loom-WI-1692` on branch `work/1692-controlled-merge-closeout-run`.
  - PR scope remains #1692.
- Purity or scope constraints:
  - Code ownership is limited to `tools/loom.py` and `tools/check_cli_contract.py`.
  - Carrier writes are limited to WI-1692 facts needed for review/merge gates.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group merge-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group closeout-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group controlled-merge`
  - `git diff --check`
- Manual checks:
  - Diff review for no default merge behavior expansion.
  - PR metadata readback for issue/branch/head consistency.
- Runtime evidence:
  - PR #1707 hosted checks.
- Behavior evidence:
  - `assert_merge_closeout_run_wrapper_contract`.
- Story scenario to evidence mapping:
  - Spec scenarios map directly to contract tests.
- Story readiness consumed:
  - No separate story readiness artifact is required.
- Story business confirmation locator:
  - No business-domain behavior is changed.
- Scenario validation mapping:
  - S1 -> automated wrapper contract.
  - S2 -> automated wrapper contract.
  - S3 -> automated wrapper contract.
  - S4 -> automated wrapper contract.
- Fresh verification evidence:
  - Local validation run on branch `work/1692-controlled-merge-closeout-run` at head `f60c6b9ae58c0290fb18c0c1f71f66aa7be5c618`.
- Execution ledger plan locator:
  - `.loom/specs/WI-1692/plan.md`
- Execution ledger validation evidence locator:
  - `.loom/progress/WI-1692.md`

## Test Strategy

- TDD or test-first expectation:
  - Add focused wrapper regression around the new CLI contract.
- Regression coverage to add or preserve:
  - Default merge wrapper delegation.
  - Inline closeout-run.
  - Host-only closeout.
  - Upgraded mode fail-closed.
  - Controlled merge block prevents closeout.
- Cases that are intentionally not automated:
  - Real GitHub merge and issue closeout, covered by hosted checks and controlled merge path.
- How failing tests or equivalent checks will be introduced before implementation:
  - Contract tests assert expected delegation and no PR creation side effects.
- How passing tests or equivalent checks will be captured as test evidence:
  - Local command output and PR validation summary.
- Acceptance test mapping:
  - A1 -> test evidence: merge wrapper contract.
  - A2 -> test evidence: merge closeout-run inline branch.
  - A3 -> test evidence: merge closeout-run host-only branch.
  - A4 -> test evidence: full closeout fail-closed branch.
  - A5 -> test evidence: local targeted validation list.
- How User Story acceptance scenarios map to tests, checks, or manual validation:
  - No separate User Story exists for this internal CLI transition; spec scenarios map directly to tests.

## Subagent Output Integration

- Owned outputs:
  - Aquinas provided read-only implementation plan for #1692.
  - Dirac provided read-only downstream #1694 documentation/fixture inventory.
- Integration owner:
  - Main agent.
- Required evidence from each subagent:
  - Summary of relevant code paths and recommended write scope.
- Review or reconciliation needed before merge-ready:
  - Main agent review record for current head and PR metadata readback.
- Handoff notes locator:
  - Current Codex thread and issue #1692 workspace_entry comment.

## Dependencies

- Blocking inputs:
  - #1695 closeout policy is closed and consumed.
- Required coordination:
  - #1694 must update docs/skills after #1692 lands.
- Rollback boundary:
  - Revert PR #1707; existing merge wrapper behavior remains available without `--closeout-run`.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly not required
- [x] Story business semantics are confirmed or explicitly not required
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or are explicitly not required
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has rationale and recheck condition
- [x] Risks and dependencies are explicit
