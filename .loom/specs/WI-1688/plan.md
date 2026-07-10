# WI-1688 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1688`
- Consumes:
  - Spec locator: `.loom/specs/WI-1688/spec.md`
  - Scenario ids / locators: S1, S2
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: N/A
  - Story Business Confirmation consumed state: N/A
- Produces:
  - Validation strategy by scenario: output envelope tests and focused CLI contract surfaces
  - Test strategy by acceptance: regression tests in `test/output_envelope_test.py` and contract checks in `tools/check_cli_contract.py`
  - Fresh verification evidence expectation: `.loom/specs/WI-1688/evidence-map.md`
- Locator:
  - Plan locator: `.loom/specs/WI-1688/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: issue #1688 and `.loom/specs/WI-1688/spec.md`
  - Freshness rule: Re-run focused checks after output envelope or wrapper changes.

## Implementation Goal

- Deliver a compact root CLI output path for non-passing actionable payloads.
- Preserve original payloads through artifacts and `--full-output`.
- Update contract consumers that must read the runtime payload from the artifact.

## Deferred Items

- None.

## Excluded Items

- Product-domain story readiness: N/A because #1688 is a bounded CLI hardening work item.
- Release publication: N/A for this PR; milestone release remains owned by #1696.

## Phases

### Phase 1

- Objective: Add generic actionable finding extraction in `tools/loom.py`.
- Deliverable: `actionable_findings` appears in compact envelopes for non-passing payloads.
- Exit condition: `test/output_envelope_test.py` covers non-budget and over-budget behavior.

### Phase 2

- Objective: Update contract tests that consume compacted wrapper output.
- Deliverable: affected closeout queue contract assertions unwrap agent-safe artifacts before checking runtime payloads.
- Exit condition: focused CLI contract surfaces pass.

## Constraints

- Architectural or governance constraints: Do not change delegated gate semantics or payload schemas.
- Workspace / rollout constraints: Work stays on branch `work/1688-minimal-action-feedback` in `/Users/mc/dev/Loom-WI-1688`.
- Purity or scope constraints: No `loom ship` implementation, no closeout policy change, no host mutation beyond issue workspace/comment readback already performed.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py test/output_envelope_test.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`
- Manual checks: Inspect diff for scope containment.
- Runtime evidence: Root wrapper behavior exercised by output tests and CLI contract subprocesses.
- Behavior evidence: `tools/loom.py` actionable envelope helpers and wrapper calls.
- Story scenario to evidence mapping: N/A; scenarios are in `spec.md`.
- Scenario validation mapping:
  - S1 -> automated
  - S2 -> automated
- Fresh verification evidence: `.loom/specs/WI-1688/evidence-map.md`

## Test Strategy

- TDD or test-first expectation: Add regression tests around output envelope behavior and then adjust implementation.
- Regression coverage to add or preserve: Preserve over-budget envelope behavior, `--full-output`, and contract artifact readback.
- Cases that are intentionally not automated: Exact English phrasing of every delegated runtime finding is not frozen.
- How failing tests or equivalent checks will be introduced before implementation: Existing output tests and governance-closeout contract exposed failures during the implementation loop.
- How passing tests or equivalent checks will be captured as test evidence: Commands listed in Validation and evidence map rows.
- Acceptance test mapping:
  - A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
  - A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
  - A3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
  - A4 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
  - A5 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- A1 -> `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
- A2 -> `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
- A3 -> `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
- A4 -> `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
- A5 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`

## Subagent Output Integration

- Owned outputs: N/A; subagent spawn was attempted but unavailable because the agent thread limit was reached.
- Integration owner: main agent.
- Required evidence from each subagent: N/A.
- Review or reconciliation needed before merge-ready: standard review and merge-ready gates.
- Handoff notes locator, or N/A: N/A.

## Dependencies

- Blocking inputs: #1686 completed; stale #1688 blocked-by edge was removed before implementation.
- Required coordination: #1694 remains downstream and blocked by #1688.
- Rollback boundary: Revert `tools/loom.py`, `tools/check_cli_contract.py`, and `test/output_envelope_test.py` changes for this PR.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly N/A
- [x] Story business semantics are confirmed or explicitly N/A
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or N/A
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has N/A rationale and recheck condition
- [x] Risks and dependencies are explicit
