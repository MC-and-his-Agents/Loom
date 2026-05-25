# Plan

## Implementation Goal

Update Loom positioning and evidence docs for #1013 while preserving the scope boundary around follow-up FRs.

## Phases

### Phase 1

- Objective: Record SDD positioning and spec-suite boundary.
- Deliverable: Updated `VISION.md`, `README.md`, and `docs/methodology/templates/spec-suite.md`.
- Exit condition: Docs say SDD is an internal execution discipline and not an SDD-only replacement.

### Phase 2

- Objective: Record spec-kit absorption evidence and landing map.
- Deliverable: `EXT-0061`, `EXT-0062`, `EXT-0063` and corresponding landing-map rows.
- Exit condition: keep/adapt/drop judgments are present and mapped.

### Phase 3

- Objective: Bind the PR to the correct repo-local Work Item.
- Deliverable: `WI-1013` carriers, review records, and PR body `Loom Work Item: WI-1013`.
- Exit condition: PR gate consumes the current Work Item instead of stale `WI-1001`.

## Constraints

- Architectural or governance constraints: do not implement #1014, #1015, #1016, or later FR content in this batch.
- Workspace / rollout constraints: branch `work/1013-sdd-operating-layer-boundary`, PR #1054.
- Purity or scope constraints: no `docs/spec-kit/*`, no `.specify/`, no copied `/speckit.*` commands.

## Validation

- Automated checks: `git diff --check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Manual checks: confirm `EXT-0061` / `EXT-0062` / `EXT-0063` appear once in ledger and landing map; confirm no copied spec-kit surfaces.
- Runtime evidence: not_applicable.
- Behavior evidence: docs and issue comments show the boundary is consumable.
- Story scenario to evidence mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; governance boundary clarification.
- Fresh verification evidence: PR #1054 head plus review record.
- Execution ledger plan locator: `.loom/specs/WI-1013/plan.md`
- Execution ledger validation evidence locator: `.loom/progress/WI-1013.md`

## Test Strategy

- TDD or test-first expectation: not_applicable for documentation-only governance boundary work.
- Regression coverage to add or preserve: source contract-only `loom_check` and targeted ledger/map checks.
- Cases that are intentionally not automated: product judgment that SDD should be internalized, already confirmed by user in thread.
- How failing tests or equivalent checks will be introduced before implementation: not_applicable.
- How passing tests or equivalent checks will be captured as test evidence: `.loom/progress/WI-1013.md`, PR #1054, and issue comments.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence: not_applicable.

## Dependencies

- Blocking inputs: #1013 scope and user confirmation that SDD can be internalized.
- Required coordination: #1014, #1015, #1016 consume this boundary after merge.
- Rollback boundary: revert this PR if SDD boundary wording conflicts with Loom's operating-layer constitution.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
