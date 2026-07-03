# WI-1904 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: existing adoption/workstation contracts already define the authority boundary and this batch changes a bounded CLI surface with focused fixtures. consumer boundary: suite validate, review, PR gate, controlled merge, closeout, and FR-4 issue closeout may consume this minimal suite plus focused CLI contract validation. recheck condition: require full suite artifacts if scope expands into destructive multi-repo mutation, release publishing, host-private Codex APIs, or FR-5 migration apply.
- Consumes:
  - Spec locator: .loom/specs/WI-1904/spec.md.
  - Scenario ids / locators: S1-S4 in spec.
  - Acceptance ids / locators: A1-A6 in spec.
  - Story Readiness consumed state: n/a; FR/WI issue bodies define the batch.
  - Story Business Confirmation consumed state: n/a; no external business semantics.
- Produces:
  - Validation strategy by scenario: focused workstation registry CLI contract plus adjacent host metadata checks.
  - Test strategy by acceptance: extend `tools/check_cli_contract.py --surface workstation-registry`.
  - Fresh verification evidence expectation: local commands at final batch head and hosted PR gates.
- Locator:
  - Plan locator: .loom/specs/WI-1904/plan.md.
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1904/spec.md; issues #1904-#1907.
  - Freshness rule: stale after any workstation CLI, registry schema, host/plugin freshness, or repo apply boundary change.

## Implementation Goal

Deliver one FR-4 batch PR covering #1904, #1905, #1906, and #1907. This PR must not defer #1906, must not reduce FR-5, and must not introduce automatic multi-repository mutation.

## Scope Retained Items

#1906 remains in scope for this batch. FR-5 migration apply/validation remains in the milestone and is preserved for the following FR-5 batch.

## Omitted Full Suite Items

### Full Suite Artifacts

- Locator: suite-index.md, research.md, contracts.md, readiness-checklist.md.
- Rationale: existing adoption/workstation contracts already define the authority boundary; this batch changes a bounded CLI surface and fixtures.
- Recheck condition: scope expands into destructive multi-repo mutation, release publishing, host-private Codex APIs, or FR-5 migration apply.
- Consumers that should not require it: suite validate, review, PR gate, merge-ready, closeout for this bounded batch.

## Phases

### Phase 1

- Objective: Make the workstation plan explicit enough for #1904/#1905/#1907.
- Deliverable: machine plan steps, repo classifications, and freshness cache fields in `tools/loom.py`; fixture/docs updates.
- Exit condition: workstation registry surface covers S1/S2/S4/A1/A2/A5/A6.

### Phase 2

- Objective: Implement bounded apply behavior for #1906.
- Deliverable: `workstation upgrade --apply` machine refresh plus explicit single-target repo apply.
- Exit condition: workstation registry surface covers S3/S4/A3/A4 and proves no implicit repo mutation.

### Phase 3

- Objective: Final batch verification and single carrier closeout.
- Deliverable: local validation, one review/shadow refresh, PR metadata, hosted checks, controlled merge, and closeout for #1904-#1907.
- Exit condition: all covered issues have closeout evidence after merge.

## Constraints

- Do not mutate registered repositories unless `--target <repo>` is explicitly supplied to `workstation upgrade --apply`.
- Do not write Loom runtime, plugin, or skills payload into target repositories.
- Do not mark `repo_pr_required` or `blocked` as auto-apply eligible.
- Do not refresh progress/status/review/shadow repeatedly while code is still moving; do final carrier refresh after implementation and validation stabilize.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
  - `git diff --check`
  - `python3 tools/check_cli_contract.py --surface workstation-registry`
  - `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- Manual checks: inspect representative `loom workstation upgrade --plan --to 0.27.0 --json` output for schema, machine plan, and freshness cache.
- Runtime evidence: none before PR; hosted PR checks provide post-push evidence.
- Scenario validation mapping:
  - S1 -> automated test evidence: `python3 tools/check_cli_contract.py --surface workstation-registry`.
  - S2 -> automated test evidence: `python3 tools/check_cli_contract.py --surface workstation-registry`.
  - S3 -> automated test evidence: `python3 tools/check_cli_contract.py --surface workstation-registry`.
  - S4 -> automated test evidence: `python3 tools/check_cli_contract.py --surface workstation-registry`.
- Fresh verification evidence: final command outputs in PR body/review record.
- Execution ledger plan locator: .loom/specs/WI-1904/plan.md.

## Test Strategy

- TDD expectation: add/extend workstation registry contract assertions before broad validation.
- Regression coverage to add or preserve:
  - Plan-only output remains non-mutating.
  - Apply output is mutating only at machine level unless explicit target is present.
  - Single-target repo apply does not write forbidden plugin/runtime payload.
  - Freshness cache exposes reuse and invalidation semantics.
- Cases intentionally not automated:
  - Real global npm installation; test uses `LOOM_TEST_WORKSTATION_APPLY=record`.
  - Codex marketplace UI refresh; CLI output records guidance and host doctor fallback.
- Acceptance test mapping:
  - A1 -> test evidence: workstation-registry surface machine step assertions.
  - A2 -> test evidence: workstation-registry surface classification assertions.
  - A3 -> test evidence: workstation-registry surface machine apply assertions.
  - A4 -> test evidence: workstation-registry surface explicit repo apply assertions.
  - A5 -> test evidence: workstation-registry surface freshness cache assertions.
  - A6 -> test evidence: workstation registry contract/docs/fixture assertions plus adoption-host-metadata surface.

## Subagent Output Integration

- Owned outputs: none; no subagent implementation output is consumed for this batch so far.
- Integration owner: main thread.
- Required evidence from each subagent: none.
- Review or reconciliation needed before merge-ready: main thread review and final carrier refresh.
- Handoff notes locator, or n/a: n/a unless the thread is interrupted.

## Dependencies

- Blocking inputs: #1903 is closed and provides plan-only baseline.
- Required coordination: PR body must list #1904, #1905, #1906, and #1907 as covered Work Items.
- Rollback boundary: one FR-4 batch PR over workstation upgrade CLI/tests/docs.

## Ready For Implementation

- [x] Spec is stable enough to implement.
- [x] Scope and non-goals are clear.
- [x] Story Readiness is confirmed or explicitly n/a.
- [x] Story business semantics are confirmed or explicitly n/a.
- [x] Validation path is defined.
- [x] BDD outer-loop scenarios map to validation.
- [x] TDD inner-loop expectations map to test evidence.
- [x] Every required scenario / acceptance mapping is present.
- [x] Risks and dependencies are explicit.
