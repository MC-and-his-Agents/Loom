# Plan

## Implementation Goal

Deliver the v0.8.0 baseline repair required before FR-scoped implementation batches can be reviewed or merged.

## Phases

### Phase 1

- Objective: remove demo bootstrap path and branch volatility.
- Deliverable: portable bootstrap output mode and `make loom-demo-new-project` using it.
- Exit condition: repeated demo bootstrap runs stabilize the checked-in fixture.

### Phase 2

- Objective: activate the real v0.8.0 Work Item.
- Deliverable: `WI-561` work item, recovery, review, status, spec, plan, and implementation contract carriers.
- Exit condition: root status resolves `WI-561` and no longer treats `INIT-0001` as active.

## Constraints

- Keep the branch bound to `#531` / `#561`.
- Preserve `INIT-0001` as historical bootstrap evidence instead of deleting it.
- Do not close GitHub child issues from this baseline repair; close them only with their FR implementation PR.

## Validation

- Automated checks: `make loom-demo-new-project`, `python3 tools/skills_surface.py check`, `python3 tools/loom_status.py --target . --item WI-561`, `make check`.
- Manual checks: inspect git status after repeated bootstrap runs.
- Runtime evidence: not applicable.
- Behavior evidence: root status and demo bootstrap idempotence.
- Fresh verification evidence: current branch `HEAD` after all baseline edits.
- Execution ledger plan locator: `.loom/specs/WI-561/plan.md`.
- Execution ledger validation evidence locator: `make check`.

## Test Strategy

- Preserve existing repo checks.
- Add the smallest new automated guard by making the existing demo bootstrap target write portable metadata.
- Use repeated local command runs to catch branch/path drift before review.

## Ready For Implementation

- [x] Spec is stable enough to implement.
- [x] Scope and non-goals are clear.
- [x] Validation path is defined.
- [x] BDD outer-loop scenarios map to validation.
- [x] TDD inner-loop expectations map to existing repository checks.
- [x] Risks and dependencies are explicit.
