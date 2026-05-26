# WI-1032 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: not_applicable; no separate full suite index is needed for this docs-only methodology change.
- Consumes:
  - Spec locator: .loom/specs/WI-1032/spec.md
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: #1029/#1030/#1031 completed upstream; this WI consumes their stable vocabulary and locator boundary.
  - Story Business Confirmation consumed state: #1029/#1030/#1031 completed upstream; this WI consumes their stable vocabulary and locator boundary.
- Produces:
  - Validation strategy by scenario: focused structural checks and contract-only loom_check.
  - Test strategy by acceptance: docs/template diff inspection and PR checks.
  - Fresh verification evidence expectation: local commands plus GitHub checks on PR head.
- Locator:
  - Plan locator: .loom/specs/WI-1032/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: #1032, #1015, #1029, #1030, #1031
  - Freshness rule: rerun validation after final commit and again consume PR checks before merge.

## Implementation Goal

- Update spec-suite entry rules so formal spec shaping can only consume confirmed or rationale-backed `not_applicable` story semantics.
- Update docs scaffold fields so spec/plan/full-suite-index record Story Readiness and Business Confirmation consumed state.
- Terminalize inherited #1031 progress carrier after PR #1098 closeout so this worktree has a single active Work Item.
- Keep runtime/generated surface changes deferred to #1020 unless validation proves a source-surface drift.

## Phases

### Phase 1

- Objective: Update source methodology and template scaffolds.
- Deliverable: `spec-suite.md`, docs `spec.md`, `plan.md`, `full-suite-index.md`.
- Exit condition: focused rg shows Story Readiness / Business Confirmation / pending / revision-requested / not_applicable rules in the expected source docs.

### Phase 2

- Objective: Bind WI-1032 local carriers and validation evidence.
- Deliverable: `.loom/work-items/WI-1032.md`, `.loom/progress/WI-1032.md`, `.loom/specs/WI-1032/*`, refreshed current status.
- Exit condition: reconciliation and contract-only loom_check pass.

### Phase 3

- Objective: PR, merge, and closeout.
- Deliverable: PR linked to #1032, checks passed, issue/project/FR comments updated after merge.
- Exit condition: #1032 closed completed, Project Done, #1015 progress updated.

## Constraints

- Do not redefine story intake contract; consume #1029-#1031.
- Do not implement #1019 gate-chain runtime enforcement here.
- Do not update generated skills/runtime surfaces unless the source-surface contract requires it.
- Work only in `/Users/mc/dev/Loom-1032-story-readiness-spec-suite` on `work/1032-story-readiness-spec-suite`.

## Validation

- Automated checks:
  - `git diff --check`
  - `python3 tools/loom_flow.py reconciliation audit --target . --issue 1032 --project 4`
  - `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Manual checks:
  - `rg -n "Story Readiness|Business Confirmation|formal spec|spec.md|plan.md|pending|revision-requested|not_applicable" docs/methodology docs skills src .loom`
- Runtime evidence: not_applicable
- Behavior evidence: source docs and scaffold diffs.
- Story scenario to evidence mapping: not_applicable.
- Story readiness consumed: #1029/#1030/#1031 completed upstream.
- Story business confirmation locator or `not_applicable` rationale: #1029/#1030/#1031 completed upstream.
- Fresh verification evidence: local validation after final commit and PR checks.
- Execution ledger plan locator: .loom/specs/WI-1032/plan.md
- Execution ledger validation evidence locator: pending until validation passes.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly `not_applicable`
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
