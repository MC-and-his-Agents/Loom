# WI-1961 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1961 is a bounded gate stabilizer batch for #1961/#1963 with implementation already constrained by the v0.28.0 temporary low-friction execution strategy; consumer boundary: suite validate, implementation review, PR metadata, hosted checks, PR gate, controlled merge, and issue closeout may consume spec, plan, implementation contract, evidence map, task carrier, local validation, and PR readback without treating skipped full-suite artifacts as completed; recheck condition: require full suite artifacts if the PR expands into host tax core, migration, release, credentials, permissions, or external write automation.
- Consumes:
  - Spec locator: `.loom/specs/WI-1961/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: not required; #1935/#1961/#1963 plus this thread's strategy define the accepted scope.
  - Story Business Confirmation consumed state: not required; this is internal process-cost reduction with no user-facing product promise beyond Loom gate/profile behavior.
- Produces:
  - Validation strategy by scenario: targeted contract checks, aggregate CLI contract check, skills release-check, PR metadata readback, and hosted checks.
  - Test strategy by acceptance: fixture updates in `tools/check_cli_contract.py` and runtime/plugin/package checks.
  - Fresh verification evidence expectation: `.loom/progress/WI-1961.md` latest validation summary and PR #1970 check readback.
- Locator:
  - Plan locator: `.loom/specs/WI-1961/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: `.loom/specs/WI-1961/spec.md`, #1961, #1963, #1935, PR #1970.
  - Freshness rule: refresh validation and review after changes to PR metadata parser/render/update/readback, review disposition matching, ship validation profile routing, generated runtime copies, or plugin payload hash.

## Implementation Goal

Deliver the gate stabilizer PR for #1961/#1963 before the larger v0.28.0 host tax core work.

Explicitly deferred:

- Default light-governance host mode.
- Installed-state slimdown.
- Current pointer and runtime ledger migration.
- Host-only closeout default.
- Batch implementation/closeout support.
- Host planning taxonomy mapping.
- Existing host slim migration.
- v0.28.0 release.

## Deferred Items

### Host Tax Core

- Locator: #1957, #1958, #1959, #1960.
- Reason: these items share a later validation boundary and should consume the gate stabilizer first.
- Activation condition: PR #1970 merged and hosted checks pass.
- Does not currently block: #1961/#1963 gate stabilizer merge.
- Statement: deferred is not completed.

### Batch, Taxonomy, Migration, Release

- Locator: #1962, #1964, #1965, #1966.
- Reason: these have different rollback and validation boundaries.
- Activation condition: host tax core merge and issue-specific readiness.
- Does not currently block: #1961/#1963 gate stabilizer merge.
- Statement: deferred is not completed.

## Skipped Full Suite Items

### Full Suite Artifacts

- Locator: suite-index.md, research.md, contracts.md, readiness-checklist.md.
- Rationale: this PR is a bounded stabilizer with concrete tests and no broad product discovery.
- Recheck condition: require full suite artifacts if scope expands into new adoption defaults, migration semantics, release automation, credentials, or external live writes.
- Consumers that should not require it: suite validate, implementation review, PR gate, hosted checks, and issue closeout for PR #1970.

## Phases

### Phase 1

- Objective: Remove volatile PR head binding from authored metadata.
- Deliverable: Template/repo-interface/parser/test updates that keep branch and Work Item as stable body fields.
- Exit condition: `pr-metadata` and `pr-gate-target-readback` contract surfaces pass.

### Phase 2

- Objective: Stabilize review and host profile validation.
- Deliverable: validation summary digest/source/locator consumption and `host-consumer` / `carrier-only` profile routing.
- Exit condition: `governance-closeout`, `merge-wrapper`, and `ship-wrapper` surfaces pass.

### Phase 3

- Objective: Sync generated runtime/plugin surfaces and pass PR metadata readback.
- Deliverable: copied runtime files, plugin payload hash, PR body machine carrier, and current `WI-1961` carrier.
- Exit condition: `aggregate`, `skills release-check`, PR metadata readback, and hosted checks pass.

## Constraints

- Do not hardcode WebEnvoy label taxonomy into core.
- Do not require downstream repositories to add repo-local `tools/loom.py`.
- Do not restore authored PR body `head_sha`.
- Do not use per-WI full old Loom closeout for #1963; #1963 is covered by the #1961 anchor PR.
- Do not expand this PR into #1957/#1958/#1959/#1960/#1962/#1964/#1965/#1966.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py examples/new-project/.loom/bin/loom_flow.py tools/loom.py tools/check_cli_contract.py`
  - `git diff --check`
  - `python3 tools/check_cli_contract.py --surface pr-metadata`
  - `python3 tools/check_cli_contract.py --surface ship-wrapper`
  - `python3 tools/check_cli_contract.py --surface pr-gate-target-readback`
  - `python3 tools/check_cli_contract.py --surface controlled-merge`
  - `python3 tools/check_cli_contract.py --surface governance-closeout`
  - `python3 tools/check_cli_contract.py --surface merge-wrapper`
  - `python3 tools/check_cli_contract.py --surface aggregate`
  - `python3 tools/loom.py skills release-check --json`
- Manual checks:
  - PR #1970 body readback confirms Work Item and branch bindings with no authored `head_sha`.
  - Hosted failure classification confirms old-body/current-pointer failures before rerun.
- Runtime evidence:
  - Generated runtime and plugin payload hashes are refreshed in repo carriers.
- Behavior evidence:
  - `tools/check_cli_contract.py` fixtures exercise the new metadata/profile behavior.
- Story scenario to evidence mapping:
  - S1 -> `pr-metadata`, `pr-gate-target-readback`, PR metadata readback.
  - S2 -> `governance-closeout`, `merge-wrapper`, review artifact.
  - S3 -> `ship-wrapper`.
- Story readiness consumed: not required; issue tree and thread strategy are scope authority.
- Story business confirmation locator: not required; internal delivery-cost reduction.
- Scenario validation mapping:
  - S1 -> automated + PR readback.
  - S2 -> automated + review artifact.
  - S3 -> automated.
- Fresh verification evidence: `.loom/progress/WI-1961.md`.
- Execution ledger plan locator: `.loom/specs/WI-1961/plan.md`.
- Execution ledger validation evidence locator: `.loom/specs/WI-1961/evidence-map.md`.

## Test Strategy

- TDD or test-first expectation: Update contract fixtures before accepting implementation behavior as complete.
- Regression coverage to add or preserve: PR metadata parser/render/update/readback, PR gate target readback, ship wrapper validation profile routing, governance closeout review consumption, merge wrapper review consumption, aggregate release-check.
- Cases that are intentionally not automated: Hosted PR body edit timing is classified through PR/readback evidence and check reruns.
- How failing tests or equivalent checks will be introduced before implementation: Existing tests failed on removed `head_sha`, raw validation summary binding, and profile choices until implementation and fixtures were updated.
- How passing tests or equivalent checks will be captured as test evidence: `.loom/progress/WI-1961.md` latest validation summary and PR #1970 checks.
- Acceptance test mapping:
  - A1: test evidence -> `pr-metadata`, PR template scan.
  - A2: validation evidence -> PR #1970 metadata readback.
  - A3: test evidence -> `governance-closeout`, `merge-wrapper`.
  - A4: test evidence -> `ship-wrapper`.
  - A5: validation evidence -> aggregate + skills release-check + hosted checks.
- How User Story acceptance scenarios map to tests, checks, manual validation, or skipped evidence: no separate User Story artifact is required for this internal stabilizer.

## Subagent Output Integration

- Owned outputs: none.
- Integration owner: main controller thread.
- Required evidence from each subagent: not required.
- Review or reconciliation needed before merge-ready: current-head review artifact for WI-1961 and PR metadata readback.
- Handoff notes locator: not required.

## Dependencies

- Blocking inputs: PR #1970 body must carry valid machine metadata; hosted checks must be rerun after PR body repair.
- Required coordination: #1963 closeout evidence must reference PR #1970 coverage rather than a separate implementation PR.
- Rollback boundary: revert PR #1970 as a unit if metadata/profile gate behavior regresses.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly not required
- [x] Story business semantics are confirmed or explicitly not required
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or skipped evidence
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has skipped-scope rationale and recheck condition
- [x] Risks and dependencies are explicit
