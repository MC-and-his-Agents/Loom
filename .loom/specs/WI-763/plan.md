# Plan

## Implementation Goal

Deliver a Loom self-governance hardening path that makes semantic review approval host-enforceable for PR merges without changing the default semantic review engine or treating raw review output as approval truth.

Deferred:

- making Codex App review the default review engine
- replacing GitHub branch protection or rulesets
- adding a separate review engine

## Phases

### Phase 1

- Objective: define the PR merge gate contract and regression evidence.
- Deliverable: `docs/methodology/harness/pr-merge-gate.md`, PR #762 evidence, extraction ledger and landing map entries.
- Exit condition: the contract names inputs, outputs, failure taxonomy, host enforcement proof, and raw evidence boundary.

### Phase 2

- Objective: implement the PR gate and controlled merge commands.
- Deliverable: `pr-gate check`, `controlled-merge check|merge`, generated skill surfaces, host workflow.
- Exit condition: installed-runtime fixtures prove fresh allow passes and missing/stale/non-allow/raw-evidence-only cases fail closed.

### Phase 3

- Objective: enforce the new gate on Loom PRs.
- Deliverable: live PR check run, branch protection or ruleset readback requiring `loom-pr-merge-gate`, controlled merge proof.
- Exit condition: #763 and child issues contain validation, live readback, residual risks, and rollback path.

## Constraints

- Preserve `loom/default-codex` and `codex exec --output-schema` as the default review path.
- Keep raw App review and shadow review output as runtime evidence only.
- Keep merge-ready consuming authored Loom review records, not raw/shadow artifacts.
- Do not replace GitHub branch protection, CI, or `gh pr merge`.
- Keep host enforcement proof separate from workflow-file existence.

## Validation

- Automated checks:
  - `python3 -m py_compile` for touched runtime entrypoints
  - `python3 tools/loom_check.py .`
  - `make skills-check`
  - `git diff --check`
- Manual checks:
  - branch protection/ruleset readback before and after enforcement
  - PR check run readback for `loom-pr-merge-gate`
- Runtime evidence:
  - installed-runtime fixtures in `loom_check.py`
  - controlled merge dry-run payload
- Behavior evidence:
  - PR #762 regression evidence record
  - GitHub issue checkpoint comments
- Fresh verification evidence:
  - `.loom/progress/WI-763.md`
- Execution ledger plan locator:
  - `.loom/specs/WI-763/plan.md`
- Execution ledger validation evidence locator:
  - `.loom/progress/WI-763.md`

## Test Strategy

- TDD or test-first expectation: add fail-closed fixtures before relying on live host enforcement.
- Regression coverage to add or preserve:
  - default review path still uses `loom/default-codex`
  - fresh authored allow passes PR gate
  - missing/stale/non-allow authored review blocks PR gate
  - raw-evidence-only bypass blocks PR gate
  - controlled merge blocks when `loom-pr-merge-gate` is not required
- Cases that are intentionally not automated:
  - final branch protection/ruleset mutation is proven by live readback rather than local fixture only.
- How failing tests or equivalent checks will be introduced before implementation:
  - `loom_check.py` installed-runtime negative fixtures.
- How passing tests or equivalent checks will be captured as test evidence:
  - `loom_check.py` full run and issue checkpoint comments.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence:
  - spec scenarios map to installed-runtime fixtures and live host readback.

## Subagent Output Integration

- Owned outputs: not_applicable.
- Integration owner: current Codex thread.
- Required evidence from each subagent: not_applicable.
- Review or reconciliation needed before merge-ready: authored Loom review record for WI-763 and PR-head-bound `loom-pr-merge-gate` pass.
- Handoff notes locator, or `not_applicable`: `.loom/progress/WI-763.md`.

## Dependencies

- Blocking inputs:
  - GitHub credentials with permission to update branch protection or ruleset.
  - live PR check run for `loom-pr-merge-gate`.
- Required coordination:
  - update #763 and child issues after each checkpoint.
- Rollback boundary:
  - remove `loom-pr-merge-gate` from branch protection/rulesets before reverting workflow/runtime files.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
