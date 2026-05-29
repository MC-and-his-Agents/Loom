# Plan

## Suite Contract

- Suite path consumed: minimal
- Full suite artifact skip is consumed from .loom/specs/WI-1143/spec.md.
- Consumes:
  - Spec locator: .loom/specs/WI-1143/spec.md
  - Scenario ids / locators: S1-S4 in .loom/specs/WI-1143/spec.md
  - Acceptance ids / locators: A1-A5 in .loom/specs/WI-1143/spec.md
  - Story Readiness consumed state: #1143 issue body
  - Story Business Confirmation consumed state: skipped for governance-only behavior
- Produces:
  - Validation strategy by scenario: direct reconciliation taxonomy contract assertions.
  - Test strategy by acceptance: tools/check_cli_contract.py plus local gate chain.
  - Fresh verification evidence expectation: .loom/progress/WI-1143.md
- Locator:
  - Plan locator: .loom/specs/WI-1143/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1143/spec.md, #1143
  - Freshness rule: update validation summary after final local checks.

## Implementation Goal

- Add a reconciliation audit suite drift mapping that consumes the same closeout suite gate evidence already used by closeout.
- Keep suite drift as blocking audit evidence; do not add safe-sync host write actions for suite drift.

## Future Items

### Future Item 1

- Locator: docs/methodology/harness/full-spec-suite-cli-surface.md `suite consistency analyze`
- Reason: consistency analyze is planned for later Work Items and is not required to classify current suite evidence/carrier failure taxonomy.
- Activation condition: when the canonical issue tree reaches the consistency analyze Work Item.
- Does not currently block: #1143 reconciliation taxonomy mapping.
- Statement: this future item is not completed by #1143.

## Skipped Items

### Skipped Item 1

- Locator: .loom/specs/WI-1143/consistency-analysis.md
- Rationale: #1143 maps existing suite evidence/carrier failure taxonomy and does not author a new consistency-analysis result.
- Recheck condition: if implementation starts generating consistency findings.
- Consumers that should not require it: reconciliation audit for this minimal suite.

## Phases

### Phase 1

- Objective: Classify suite gate failures in reconciliation audit.
- Deliverable: suite drift findings for stale evidence, head/PR drift, host state conflict, and missing suite gate.
- Exit condition: contract assertions cover all mapped finding kinds.

### Phase 2

- Objective: Preserve generated surfaces and existing reconciliation semantics.
- Deliverable: synced skills/runtime copies and focused validation evidence.
- Exit condition: CLI contract and surface checks pass.

## Constraints

- Architectural or governance constraints: suite validation is audit evidence; Work Item, review, merge-ready, closeout, Project, and docs/source truth remain authoritative.
- Workspace / rollout constraints: issue-scoped branch/worktree/PR only.
- Purity or scope constraints: no source-specific command names, no source-specific layout, no new reconciliation host writes for suite drift.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
  - `git diff --check`
  - focused `rg` for reconciliation suite findings and forbidden source-specific command/layout surfaces
  - `python3 tools/skills_surface.py check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Manual checks: inspect reconciliation audit payload for suite drift findings when suite gate validation blocks.
- Runtime evidence: .loom/progress/WI-1143.md
- Behavior evidence: tools/check_cli_contract.py `assert_reconciliation_suite_taxonomy_contract`.
- Story scenario to evidence mapping: S1-S4 mapping below.
- Story readiness consumed: #1143 issue body.
- Story business confirmation locator: skipped for governance-only behavior.
- Scenario validation mapping:
  - S1 -> automated: stale evidence finding assertion.
  - S2 -> automated: head/PR drift finding assertion.
  - S3 -> automated: host carrier conflict finding assertion.
  - S4 -> automated: missing suite gate finding assertion.
- Fresh verification evidence: .loom/progress/WI-1143.md
- Execution ledger plan locator: .loom/specs/WI-1143/plan.md
- Execution ledger validation evidence locator: tools/check_cli_contract.py

## Test Strategy

- TDD or test-first expectation: add reconciliation taxonomy contract assertion before final validation.
- Regression coverage to add or preserve: suite drift findings plus existing parent/project/host drift behavior.
- Cases that are intentionally not automated: live GitHub Project mutations for suite drift, because suite drift must not create host writes.
- How failing tests or equivalent checks will be introduced before implementation: synthetic suite gate payloads assert the reconciliation helper returns required findings.
- How passing tests or equivalent checks will be captured as test evidence: `tools/check_cli_contract.py`.
- Acceptance test mapping:
  - A1 -> structural evidence: `reconciliation_audit_payload` includes `suite_gate_validation` for retained Work Item suites.
  - A2 -> test evidence: `suite_stale_evidence` assertion.
  - A3 -> test evidence: `suite_head_or_pr_drift` assertion.
  - A4 -> test evidence: `suite_host_state_conflict` assertion.
  - A5 -> test evidence: `missing_suite_gate` assertion and sync-plan unsupported block behavior.
- How User Story acceptance scenarios map to tests, checks, or manual validation: S1-S4 and A1-A5 map to the automated and structural checks above.

## Subagent Output Integration

- Owned outputs: main executor owns implementation.
- Integration owner: main executor.
- Required evidence from each subagent: none; no subagent owned output is consumed.
- Review or reconciliation needed before merge-ready: spec review, implementation review, PR gate, closeout.
- Handoff notes locator: not required; recovery entry remains .loom/progress/WI-1143.md.

## Dependencies

- Blocking inputs: #1143 issue body, full spec suite CLI surface, gate-chain contract, task-carrier contract.
- Required coordination: parent FR #1136 and phase #1107 progress comments after closeout.
- Rollback boundary: revert reconciliation suite finding mapping and generated sync changes.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed by #1143 issue scope
- [x] Story business semantics are skipped because this is governance-only behavior
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
