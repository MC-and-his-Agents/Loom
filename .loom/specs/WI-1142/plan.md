# Plan

## Suite Contract

- Suite path consumed: minimal
- Full suite artifact skip is consumed from .loom/specs/WI-1142/spec.md.
- Consumes:
  - Spec locator: .loom/specs/WI-1142/spec.md
  - Scenario ids / locators: S1-S3 in .loom/specs/WI-1142/spec.md
  - Acceptance ids / locators: A1-A5 in .loom/specs/WI-1142/spec.md
  - Story Readiness consumed state: #1142 issue body
  - Story Business Confirmation consumed state: skipped for governance-only behavior
- Produces:
  - Validation strategy by scenario: closeout payload assertions and negative fixture.
  - Test strategy by acceptance: tools/check_cli_contract.py plus local gate chain.
  - Fresh verification evidence expectation: .loom/progress/WI-1142.md
- Locator:
  - Plan locator: .loom/specs/WI-1142/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1142/spec.md, #1142
  - Freshness rule: update validation summary after final local checks.

## Implementation Goal

- Deliver closeout suite gate consumption for evidence/carrier validation and consumed locators.
- Leave new `suite consistency analyze` implementation to later Work Items; closeout consumes the consistency-analysis locator key that suite validation already exposes.

## Future Items

### Future Item 1

- Locator: docs/methodology/harness/full-spec-suite-cli-surface.md `suite consistency analyze`
- Reason: consistency analyze is planned for later Work Items and is not required to make closeout consume existing locator state.
- Activation condition: when the canonical issue tree reaches the consistency analyze Work Item.
- Does not currently block: #1142 closeout suite evidence/carrier validation.
- Statement: this future item is not completed by #1142.

## Skipped Items

### Skipped Item 1

- Locator: .loom/specs/WI-1142/consistency-analysis.md
- Rationale: #1142 validates the closeout consumer boundary; it does not author a new consistency analysis result.
- Recheck condition: if implementation starts generating consistency findings.
- Consumers that should not require it: closeout gate for this minimal suite.

## Phases

### Phase 1

- Objective: Wire closeout to suite gate validation.
- Deliverable: `suite_gate_validation` with surface `closeout` and required closeout subchecks.
- Exit condition: closeout blocks missing suite evidence.

### Phase 2

- Objective: Preserve contract coverage and generated surfaces.
- Deliverable: CLI contract assertions, synced skills/runtime/demo copies, and suite carriers.
- Exit condition: focused validation passes.

## Constraints

- Architectural or governance constraints: suite validation is evidence; Work Item, review, merge-ready, closeout, Project, and docs/source truth remain authoritative.
- Workspace / rollout constraints: issue-scoped branch/worktree/PR only.
- Purity or scope constraints: no `/speckit.*`, no `.specify/`, no automatic issue close without closeout evidence.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
  - `git diff --check`
  - focused `rg` for closeout suite subchecks and forbidden `/speckit` / `.specify`
  - `python3 tools/skills_surface.py check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Manual checks: inspect closeout payload for `suite_gate_validation.surface == closeout`.
- Runtime evidence: .loom/progress/WI-1142-build-evidence.json
- Behavior evidence: tools/check_cli_contract.py negative missing evidence fixture.
- Story scenario to evidence mapping: S1-S3 mapping below.
- Story readiness consumed: #1142 issue body.
- Story business confirmation locator: skipped for governance-only behavior.
- Scenario validation mapping:
  - S1 -> automated: closeout payload assertion in tools/check_cli_contract.py.
  - S2 -> automated: `assert_closeout_blocks_missing_suite_evidence`.
  - S3 -> structural: consumed locator assertions for evidence-map, consistency-analysis key, and task carriers.
- Fresh verification evidence: .loom/progress/WI-1142.md
- Execution ledger plan locator: .loom/specs/WI-1142/plan.md
- Execution ledger validation evidence locator: .loom/progress/WI-1142-build-evidence.json

## Test Strategy

- TDD or test-first expectation: add closeout contract assertion before final validation.
- Regression coverage to add or preserve: closeout suite gate pass path and missing evidence fail-closed path.
- Cases that are intentionally not automated: live GitHub Project status changes beyond normal closeout readback.
- How failing tests or equivalent checks will be introduced before implementation: remove evidence-map in preserved fixture and assert closeout blocks.
- How passing tests or equivalent checks will be captured as test evidence: `tools/check_cli_contract.py`.
- Acceptance test mapping:
  - A1 -> test evidence: `assert_suite_gate_consumption(closeout_payload, expected_surface="closeout")`.
  - A2 -> test evidence: `assert_closeout_blocks_missing_suite_evidence`.
  - A3 -> test evidence: consumed locator assertions.
  - A4 -> test evidence: `python3 tools/check_cli_contract.py`.
  - A5 -> structural check: `python3 tools/skills_surface.py check` and generated surface checks.
- How User Story acceptance scenarios map to tests, checks, or manual validation: S1-S3 and A1-A5 map to the automated and structural checks above.

## Subagent Output Integration

- Owned outputs: main executor owns implementation.
- Integration owner: main executor.
- Required evidence from each subagent: none; no subagent owned output is consumed.
- Review or reconciliation needed before merge-ready: spec review, implementation review, PR gate, closeout.
- Handoff notes locator: not required; recovery entry remains .loom/progress/WI-1142.md.

## Dependencies

- Blocking inputs: #1142 issue body, full spec suite CLI surface, evidence-map template, task-carrier contract.
- Required coordination: parent FR #1136 and phase #1107 progress comments after closeout.
- Rollback boundary: revert closeout suite subcheck wiring and generated sync changes.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed by #1142 issue scope
- [x] Story business semantics are skipped because this is governance-only behavior
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
