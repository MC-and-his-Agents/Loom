# Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator: .loom/specs/WI-1452/spec.md
- Consumes:
  - Spec locator: .loom/specs/WI-1452/spec.md
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1, A2, A3, A4, A5
  - Story Readiness consumed state: N/A; see spec rationale
  - Story Business Confirmation consumed state: N/A; see spec rationale
- Produces:
  - Validation strategy by scenario: targeted CLI contract fixtures plus hosted PR checks
  - Test strategy by acceptance: merge-wrapper and controlled-merge surfaces
  - Fresh verification evidence expectation: current PR #1614 head or accepted carrier-only drift
- Locator:
  - Plan locator: .loom/specs/WI-1452/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1452/spec.md; GitHub issue #1452; PR #1614
  - Freshness rule: refresh if runtime logic or expected allowed/blocking taxonomy changes.

- full-path-artifacts not_applicable rationale: WI-1452 uses the minimal suite because implementation is bounded to controlled-merge runtime behavior, docs, fixtures, and generated/demo sync; consumer boundary: plan validation, review, merge-ready, and closeout consume this plan plus targeted verification evidence without requiring full-path artifacts; recheck condition: expand to full suite if the work adds shared contracts, migration design, release publication, live settings mutation, or cross-repo fixture closeout.

## Implementation Goal

- Deliver triggered-check rollup consumption inside `controlled-merge` without changing required-check logic.
- Defer #1292 cross-repo fixtures, #1293 release convergence, live branch protection mutation, and parent closeout.

## Deferred Items

### Deferred Item 1

- Locator: GitHub issue #1292
- Reason: Cross-repo fixture closeout consumes #1452 behavior but has separate HotCP/WebEnvoy/Syvert coverage.
- Activation condition: #1452 PR merged and issue closed.
- Does not currently block: #1452 runtime behavior delivery.
- Statement: deferred is not completed.

### Deferred Item 2

- Locator: GitHub issue #1293
- Reason: Release convergence and v0.16.0 publication must consume completed #1452/#1292 facts.
- Activation condition: #1452 and #1292 are closed.
- Does not currently block: #1452 runtime behavior delivery.
- Statement: deferred is not completed.

## Out-of-scope Items

### Out-of-scope Item 1

- Locator: live GitHub branch protection / ruleset mutation
- Rationale: #1452 changes Loom controlled-merge product behavior only.
- Recheck condition: a follow-up live-config Work Item authorizes settings mutation.
- Consumers that should not require it: spec review, implementation review, merge-ready for PR #1614.

### Out-of-scope Item 2

- Locator: VERSION/tag/GitHub Release/npm publish
- Rationale: release is owned by #1293 after milestone work lands.
- Recheck condition: #1293 release branch starts.
- Consumers that should not require it: #1452 merge-ready and closeout.

## Phases

### Phase 1

- Objective: Add triggered-check classification and rollup output.
- Deliverable: runtime changes in `loom_flow.py` source and generated copies.
- Exit condition: allowed, failed, pending, unknown, and unreadable classifications are visible in JSON.

### Phase 2

- Objective: Add docs and fixtures.
- Deliverable: controlled-merge docs plus CLI contract fixture coverage.
- Exit condition: merge-wrapper and controlled-merge targeted surfaces pass.

### Phase 3

- Objective: Sync carriers and hosted gate inputs.
- Deliverable: demo fixture sync, WI-1452 carriers, PR metadata readback.
- Exit condition: hosted checks and controlled-merge readback pass for PR #1614.

## Constraints

- Architectural or governance constraints: required checks and triggered checks remain separate read surfaces.
- Workspace / rollout constraints: branch `work/1452-controlled-merge-triggered-checks`; PR #1614.
- Purity or scope constraints: no #1292/#1293/#1285 closeout, no live settings mutation, no release action.

## Validation

- Automated checks:
  - `python3 -m py_compile src/skills/shared/scripts/loom_flow.py tools/check_cli_contract.py examples/new-project/.loom/bin/loom_flow.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge`
  - `python3 tools/skills_surface.py check --surface generated-tree-drift`
  - `make loom-demo-new-project-check`
  - `git diff --check`
- Manual checks: PR metadata readback and hosted check classification.
- Runtime evidence: `.loom/progress/WI-1452.md`; PR #1614 status checks.
- Behavior evidence: targeted CLI fixture output and controlled-merge JSON payload.
- Story scenario to evidence mapping: S1/S2/S3 map to targeted CLI fixture surfaces.
- Scenario validation mapping:
  - S1 -> automated validation evidence: merge-wrapper fixture for required-green plus non-required failed triggered check.
  - S2 -> automated validation evidence: merge-wrapper fixture for required-green plus pending triggered check.
  - S3 -> automated validation evidence: controlled-merge fixture for allowed triggered checks.
- Story readiness consumed: N/A; see spec rationale.
- Story business confirmation: N/A; see spec rationale.
- Fresh verification evidence: must name the current PR #1614 head or carrier-only drift.
- Execution ledger plan locator: .loom/specs/WI-1452/plan.md
- Execution ledger validation evidence locator: .loom/progress/WI-1452.md

## Test Strategy

- TDD or test-first expectation: targeted fixture assertions define blocking/allowed rollup behavior.
- Regression coverage to add or preserve: required-check positive path and retained PR/merge-gate path stay passing.
- Manual-only exclusions: live GitHub settings mutation and release publication.
- How failing tests or equivalent checks will be introduced before implementation: fixture cases for failed/pending triggered checks.
- How passing tests or equivalent checks will be captured as test evidence: CLI contract surface output and hosted checks.
- Acceptance test mapping:
  - A1 -> test evidence: merge-wrapper fixture required-check assertions.
  - A2 -> test evidence: merge-wrapper non-required failed fixture.
  - A3 -> test evidence: merge-wrapper pending fixture.
  - A4 -> test evidence: controlled-merge allowed triggered fixture.
  - A5 -> test evidence: payload field assertions in `tools/check_cli_contract.py`.
- User Story acceptance mapping: N/A; scenarios are internal runtime gate cases in this suite.

## Subagent Output Integration

- Owned outputs: Lane A runtime/generated changes; Lane B docs/fixture changes; main controller carrier/PR body sync.
- Integration owner: Codex main thread.
- Required evidence from each subagent: changed locators, validation commands, boundary notes.
- Review or reconciliation needed before merge-ready: main controller review record and hosted gate readback.
- Handoff notes locator: current thread summary and `.loom/progress/WI-1452.md`

## Dependencies

- Blocking inputs: PR #1614 hosted checks and metadata readback.
- Required coordination: #1292 starts after #1452 merge; #1293 starts after #1292 merge.
- Rollback boundary: revert PR #1614 runtime/docs/fixture commits; carriers are closeout evidence only.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly N/A with rationale
- [x] Story business semantics are confirmed or explicitly N/A with rationale
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Required scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
