# WI-1481 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1481 is a bounded helper-layer Work Item with deterministic focused tests and no external host contract, research, or readiness discovery need. consumer boundary: suite validate, review, PR gate, merge-ready, dependent issues #1482/#1483/#1484/#1487, and issue closeout may consume this minimal suite plus focused test evidence for the reusable helper contract only. recheck condition: require full suite artifacts if scope expands into command-by-command integration, configurable budget policy, plugin/skill protocol changes, release execution, security/privacy policy, or external-visible host writes.
- Consumes:
  - Spec locator: .loom/specs/WI-1481/spec.md
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A3
  - Story Readiness consumed state: issue body is sufficient for this helper-layer hardening item.
  - Story Business Confirmation consumed state: no external business semantics.
- Produces:
  - Validation strategy by scenario: focused unit tests plus py_compile/diff checks.
  - Test strategy by acceptance: `test/output_envelope_test.py`.
  - Fresh verification evidence expectation: rerun focused checks at current head before PR gate.
- Locator:
  - Plan locator: .loom/specs/WI-1481/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1481/spec.md; issue #1481.
  - Freshness rule: recheck after helper API or artifact path changes.

## Implementation Goal

- Deliver the reusable helper layer needed by later high-noise command work.
- Defer command-by-command integration and configurable budget policy to dependent issues.

## Phases

### Phase 1

- Objective: Add helper functions for output envelope, artifact writing, and over-budget summary conversion.
- Deliverable: `tools/loom.py` helpers.
- Exit condition: helpers are importable and focused tests exercise normal, artifact, and over-budget paths.

### Phase 2

- Objective: Add minimal regression coverage and carriers.
- Deliverable: `test/output_envelope_test.py` and Loom suite/carrier files.
- Exit condition: focused tests, py_compile, and diff check pass.

## Constraints

- Do not change command pass/fail semantics.
- Do not restore repo-local runtime/plugin/skills paths.
- Do not make output artifacts authoritative truth carriers.
- Keep the helper API small enough for later command issues to consume without broad refactor.

## Validation

- Automated checks:
  - `python3 test/output_envelope_test.py`
  - `python3 -m unittest discover -s test -p 'output_envelope_test.py'`
  - `python3 tools/py_compile_clean.py tools/loom.py test/output_envelope_test.py`
  - `git diff --check`
- Manual checks: inspect artifact locator and JSON payload shape in focused tests.
- Runtime evidence: not required for this helper-only slice.
- Behavior evidence: .loom/specs/WI-1481/evidence-map.md
- Fresh verification evidence: rerun checks after any helper changes.
- Scenario validation mapping:
  - S1 -> automated: `test_output_envelope_contains_agent_safe_fields`
  - S2 -> automated: `test_write_output_artifact_persists_full_payload`
  - S3 -> automated: `test_agent_safe_payload_writes_artifact_when_over_budget`

## Test Strategy

- TDD or test-first expectation: focused tests define the reusable contract before command integration.
- Regression coverage to add or preserve: normal envelope, full artifact write, over-budget envelope.
- Cases that are intentionally not automated: integration into every high-noise command; covered by dependent issues.
- How passing tests or equivalent checks will be captured as test evidence: .loom/specs/WI-1481/evidence-map.md and final PR validation summary.
- Acceptance test mapping:
  - A1 -> test evidence: `test_output_envelope_contains_agent_safe_fields`
  - A2 -> test evidence: `test_write_output_artifact_persists_full_payload`
  - A3 -> test evidence: `test_agent_safe_payload_writes_artifact_when_over_budget`

## Dependencies

- Blocking inputs: none.
- Required coordination: dependent issues #1482, #1483, #1484, #1487 consume the helper contract.
- Rollback boundary: revert `tools/loom.py` helper additions, focused test, and WI-1481 carriers.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is covered by the issue body for this helper-layer item
- [x] Story business semantics do not apply to this helper-layer item
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
